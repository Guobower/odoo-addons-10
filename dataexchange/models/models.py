# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
import time
import datetime

import sys
import subprocess
import os
import os.path
import shutil
import csv


_logger = logging.getLogger(__name__)
_importers = {}
_exporters = {}

RUN_ERR_ARCHIVE = "21"
RUN_ERR_ADAPTER_NOT_FOUND = "22"
RUN_ERR_ENDPOINT_INVALID = "23"
RUN_ERR_UNKNOWN_DIRECTION = "24"
RUN_ERR_DUPLICATE_ENTRY = "25"


def registerImporter(code, importer):
    _importers[code] = importer
    _logger.info("Importer %s added", code)


def registerExporter(code, exporter):
    _exporters[code] = exporter
    _logger.info("Exporter %s added", code)


class SearchError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Adapter():

    def _search_by_name(self, env, model_name, name, col='name', case_sensitive=False):
        # FIXME: problem with i18n
        record = env[model_name].with_context(lang="fr_FR").sudo().search(
            [(col, '=ilike' if case_sensitive else "=", name)])
        if len(record) == 1:
            return record.id
        elif len(record) > 1:
            raise SearchError(
                'Many found: Model [%s], col [%s], value[%s]' % (model_name, col, name))
        else:
            return 0

    def prepare(self, env, stream):
        return True


class Exporter(Adapter):

    def extract(self, run):
        _logger.debug("Starting extraction for RUN: %s", run.name)
        return self._extract(run)

    def _extract(self, run):
        return True

    def export(self, run):
        filename = run.stream_id.endpoint_data_path
        _logger.info("Start exporting to file: %s", filename)
        data_to_export_ids = run.data_record_ids.filtered(
            lambda x: x.state != 'exported')
        return self._export(run, data_to_export_ids)

    def _export(self, run, data_to_export_ids):
        return True


class Importer(Adapter):

    def load(self, run):
        filename = run.stream_id.endpoint_data_path

        _logger.debug("Start loading file: %s", filename)
        return self._load(run, filename)

    def _load(self, run):
        return True

    def integrate(self, run):
        _logger.debug("Start integration for RUN: %s", run.name)
        data_to_integrate_ids = run.data_record_ids.filtered(
            lambda x: x.state != 'processed')
        if run.stream_id.filter_duplicates:
            self._filter_duplicates(run, data_to_integrate_ids)
        return self._integrate(run, data_to_integrate_ids)

    def _integrate(self, run, data_to_integrate_ids):
        return True

    def archive(self, run):
        input_file = run.stream_id.endpoint_data_path

        try:
            if run.stream_id.archive_mode == 'separate':
                self._archiveFile(
                    input_file, run.stream_id.archive_path, run.stream_id.archive_mask, run.start_date)
            elif run.stream_id.archive_mode == 'delete':
                self._deleteFile(input_file)
            elif run.stream_id.archive_mode == 'rename':
                self._renameFile(
                    input_file, run.stream_id.archive_mask, run.start_date)
            # Nothing to do for 'keep' method
        except:
            # TODO: Error log
            return False

        return True

    def _archiveFile(self, input_file, path, mask, date):
        if not path:
            path = ""

        try:
            if not os.path.isdir(path):
                os.makedirs(path)

            if not mask:
                mask = "%Y%m%d"

            # FIXME: use date instead of now() but date is String
            filename, file_extension = os.path.splitext(os.path.basename(
                input_file))
            new_filename = filename + "_" + datetime.datetime.now().strftime(mask) + \
                file_extension

            shutil.copy2(input_file, os.path.join(path, new_filename))
            os.remove(input_file)
        except:
            self.addLogError(
                RUN_ERR_ARCHIVE, "Impossible d'archiver le fichier %s" % input_file)

    def _renameFile(self, input_file, mask, date):
        if not mask:
            mask = "%Y%m%d"

        # FIXME: use date instead of now() but date is String
        filename, file_extension = os.path.splitext(os.path.basename(
            input_file))
        new_filename = filename + "_" + datetime.datetime.now().strftime(mask) + \
            file_extension
        try:
            os.rename(input_file, os.path.join(
                os.path.dirname(input_file), new_filename))
        except:
            self.addLogError(
                RUN_ERR_ARCHIVE, "Impossible de renommer le fichier %s " % input_file)

    def _deleteFile(self, input_file):
        try:
            os.remove(input_file)
        except:
            self.addLogError(
                RUN_ERR_ARCHIVE, "Impossible de supprimer le fichier %s" % input_file)

    def _filter_duplicates(self, run, data_to_integrate_ids):
        """
        Filter out every document processed by the importer has already been treated
        by a precedent run.
        To enable this feature the `filter_duplicates` field must be set to true in
        the Stream instance and every stream data must specify store a unique identifier
        in every StreamData's `document_id` field.
        """
        duplicate_ids = []
        for record in data_to_integrate_ids:
            for stream_run in run.stream_id.run_ids:
                if run.id != stream_run.id:
                    for data_record in stream_run.data_record_ids:
                        if record.document_id == data_record.document_id:
                            err_msg = "Duplicate entry {0} already treated in run {}" \
                                .format(record.document_id, stream_run.name)
                            self.addLogError(RUN_ERR_DUPLICATE_ENTRY, err_msg)
                            duplicate_ids.append(record.id)
        deduplicated_data = [data for data in data_to_integrate_ids if data.id not in duplicate_ids]
        # TODO: test this feature with a valid dataset
        return deduplicated_data


class StreamRun(models.Model):
    _name = "dataexchange.stream.run"
    _description = "Stream run model"
    _order = "start_date DESC"

    name = fields.Char(
        required=True,
        size=40,
        string="Libellé")

    active = fields.Boolean(default=True, required=True)

    retry_count = fields.Integer(default=0, required=True, string="Nombre de traitements",
                                 help="Nombre de lancements")

    stream_id = fields.Many2one(
        "dataexchange.stream",
        ondelete="cascade",
        string="Flux")

    state = fields.Selection(
        [("initiated", "En cours"),
         ("loaded", "Chargé"),
         ("extracted", "Extrait"),
         ("extract_err", "Extraction échouée"),
         ("load_err", "Chargement échoué"),
         ("partial", "Traitement partiel"),
         ("integrated", "Intégré"),
         ("integration_err", "Intégration échouée"),
         ("exported", "Exporté"),
         ("export_err", "Exportation échouée"),
         ("global_err", "Erreur générale"),
         ("param_err", "Erreur de paramétrage")
         ], default="initiated", required=True)

    start_date = fields.Datetime(
        required=True,
        default=fields.Datetime.now,
        string="Date/Heure de début")

    end_date = fields.Datetime(string="Date/Heure de fin")

    data_record_ids = fields.One2many(
        comodel_name="dataexchange.stream.data",
        inverse_name="run_id",
        string="Enregistrement de données"
    )

    mode = fields.Selection(
        [("manual", "Manuel"), ("auto", "Automatique")],
        default="manual",
        required=True)

    total_record_count = fields.Integer(compute='_get_record_total_count',
                                        string="Enregistrements",
                                        store=True)

    cr_ids = fields.One2many(
        "dataexchange.stream.cr", "run_id", string="Compte-rendus")

    def end(self, status=None):
        self.end_date = datetime.datetime.now()
        if status:
            self.state = status

    def addLogSuccess(self, message):
        _logger.info(message)
        self.env['dataexchange.stream.cr'].create({'message': message,
                                                   'run_id': self.id})

    def addLogError(self, message, code):
        _logger.warning(code + ":" + message)
        self.env['dataexchange.stream.cr'].create({'error_code': code,
                                                   'message': message,
                                                   'run_id': self.id})

    def addLogInfo(self, message):
        _logger.info(message)
        self.env['dataexchange.stream.cr'].create({'message': message,
                                                   'run_id': self.id})

    @api.depends('data_record_ids')
    def _get_record_total_count(self):
        for r in self:
            r.total_record_count = len(r.data_record_ids)

    @api.one
    def execute(self):
        return True

    @api.one
    def retry(self, mode):
        if (self.stream_id.direction == 'in'):
            self._retryImport(mode)
        else:
            self._retryExport(mode)

    def _retryImport(self, mode):
        if self.state != 'integrated':
            importer = self.stream_id._get_importer()

            if not importer:
                self.addLogError("No importer found for code: %s" %
                                 self.stream_id.adapter, RUN_ERR_ADAPTER_NOT_FOUND)
                return False

            self.retry_count += 1

            importer.prepare(self.env, self.stream_id)
            if importer.integrate(self):
                _logger.info("Integration retry #%i for %s succeded",
                             self.retry_count, self.name)
                return True

            _logger.warning("Integration %s failed", self.name)
            return False
        else:
            return True

    def _retryExport(self, mode):
        # TODO: export retry : what to do ?
        return True


class Stream(models.Model):
    _name = "dataexchange.stream"
    _description = "Data exchange stream definition"

    name = fields.Char(
        required=True,
        size=80,
        string="Nom")
    active = fields.Boolean(
        default=True,
        required=True)
    code = fields.Char(
        required=True,
        size=20,
        string="Code")
    direction = fields.Selection(
        [("in", "Import"), ("out", "Export")],
        required=True,
        size=10,
        string="Direction")
    endpoint = fields.Char(
        required=True,
        size=50,
        string="Partenaire")
    description = fields.Text(
        required=True,
        size=200,
        string="Description")
    comment = fields.Text(
        size=800,
        string="Commentaires")
    max_run_retry = fields.Integer(
        default="3",
        string="Nombre max tentatives",
        required=True)
    endpoint_data_path = fields.Char(
        size=200,
        string="Chemin de fichier")
    notification_email = fields.Char(
        size=200,
        string="Destinataires notifications")
    param_ids = fields.One2many(
        string="Paramètres",
        comodel_name="dataexchange.stream.parameter",

        inverse_name="stream_id")
    run_ids = fields.One2many(
        comodel_name="dataexchange.stream.run",
        inverse_name="stream_id",
        string="Exécutions")

    basename = fields.Char(size=20, string="Nom racine",
                           required=True, default="Adapter")

    adapter = fields.Char(size=20, string="Code adaptateur", required=True)

    archive_path = fields.Char(size=100, string="Chemin d'archives")

    archive_mode = fields.Selection(
        [("none", "Aucun"), ("rename", "Dans le répertoire"),
         ("separate", "Dans un autre répertoire"),
         ("delete", "Supprimer")], default="rename", required=True)

    archive_mask = fields.Char(size=20, String="Masque d'archivage")

    filter_duplicates = fields.Boolean(default=False)

    def get_param(self, paramName, defaultValue):
        recordSet = self.param_ids.filtered(
            lambda r: r.name == paramName)
        if recordSet:
            return recordSet[0].value
        else:
            return defaultValue

    def _ensure_endpoint_is_valid(self):
        return os.path.isfile(self.endpoint_data_path)

    @api.multi
    def retry_all(self):
        for record in self:
            record._retry('manual')

    @api.model
    def run_by_code(self, code, new_run, recycle_previous):
        stream_ids = self.env['dataexchange.stream'].search(
            [('code', '=', code)])

        for stream in stream_ids:
            if recycle_previous:
                stream.recycle_previous('auto')
            if new_run:
                stream.run_auto()

    @api.multi
    def run_manual(self):
        for record in self:
            record._run('manual')

    @api.multi
    def run_auto(self):
        for record in self:
            record._run('auto')

    @api.model
    def recycle_previous(self, mode):
        self._retry(mode)

    @api.one
    def run_auto_and_recycle_previous(self):
        self._run('auto')
        self._retry('auto')

    def _retry(self, mode):
        error_run_ids = self.run_ids.filtered(
            lambda x: x.state != 'integrated' and x.retry_count <= self.max_run_retry)

        for run in error_run_ids:
            run.retry(mode)

    def _run(self, mode):
        run = self._initRun(mode)
        run_result = None

        if self.direction == 'in':
            if not self._ensure_endpoint_is_valid():
                run.addLogError('Invalid endpoint file %s' %
                                self.endpoint_data_path, RUN_ERR_ENDPOINT_INVALID)
                run.end('load_err')
                return False
            run_result = self._runImport(run)
        elif self.direction == 'out':
            run_result = self._runExport(run)
        else:
            run.addLogError('Unknown direction : %s' %
                            direction, RUN_ERR_UNKNOWN_DIRECTION)
            run.end('global_err')
            return False

        if run_result:
            run.end('integrated' if self.direction == 'in' else 'exported')
            return True
        else:
            return False

    def _initRun(self, mode):
        run_start_date = datetime.datetime.now()
        run_name = self.basename + " " + \
            run_start_date.strftime("%d-%m-%Y %H:%M")

        requested_run = self.env['dataexchange.stream.run'].create({'name': run_name,
                                                                    'state': 'initiated',
                                                                    'mode': mode,
                                                                    'retry_count': 1,
                                                                    'start_date': run_start_date,
                                                                    'stream_id': self.id})

        return requested_run

    def _get_importer(self):
        return _importers.get(self.adapter, None)

    def _runImport(self, run):
        importer = self._get_importer()

        if not importer:
            run.addLogError("No importer found for code: %s" %
                            self.adapter, RUN_ERR_ADAPTER_NOT_FOUND)
            return False

        importer.prepare(run.env, self)

        if importer.load(run):
            success = True if importer.integrate(run) else False
            archive_success = True if importer.archive(run) else False is None
            if not archive_success:
                run.addLogError(
                    "Archivage du fichier source échoué", RUN_ERR_ARCHIVE)

            success &= archive_success
            return success

        _logger.error("Import %s failed", run.name)
        return False

    def _runExport(self, run):
        exporter = _exporters.get(self.adapter, None)

        if not exporter:
            _logger.error("No exporter found for code: %s", self.adapter)
            return False

        exporter.prepare(run.env, self)

        if exporter.extract(run):
            return exporter.export(run)
        else:
            return False


class StreamParameter(models.Model):
    _name = "dataexchange.stream.parameter"
    _description = "Stream parameter depending on Stream type"

    stream_id = fields.Many2one(
        comodel_name="dataexchange.stream", string="Flux")

    name = fields.Char(size=20, required=True)

    value = fields.Text(size=200, required=True)


class StreamData(models.Model):
    _name = "dataexchange.stream.data"
    _description = "Stream raw data"

    run_id = fields.Many2one(
        "dataexchange.stream.run", ondelete="cascade", required=True, string="Exécution du flux")
    # TODO: Why ?
    line_number = fields.Integer(required=True, string="Numéro")

    document_id = fields.Char(size=250)

    data_1 = fields.Char(size=250, string="Champ 1")
    data_2 = fields.Char(size=250, string="Champ 2")
    data_3 = fields.Char(size=250, string="Champ 3")
    data_4 = fields.Char(size=250, string="Champ 4")
    data_5 = fields.Char(size=250, string="Champ 5")
    data_6 = fields.Char(size=250, string="Champ 6")
    data_7 = fields.Char(size=250, string="Champ 7")
    data_8 = fields.Char(size=250, string="Champ 8")
    data_9 = fields.Char(size=250, string="Champ 9")
    data_10 = fields.Char(size=250, string="Champ 10")
    data_11 = fields.Char(size=250, string="Champ 11")
    data_12 = fields.Char(size=250, string="Champ 12")
    data_13 = fields.Char(size=250, string="Champ 13")
    data_14 = fields.Char(size=250, string="Champ 14")
    data_15 = fields.Char(size=250, string="Champ 15")
    data_16 = fields.Char(size=250, string="Champ 16")
    data_17 = fields.Char(size=250, string="Champ 17")
    data_18 = fields.Char(size=250, string="Champ 18")
    data_19 = fields.Char(size=250, string="Champ 19")
    data_20 = fields.Char(size=250, string="Champ 20")
    data_21 = fields.Char(size=250, string="Champ 21")
    data_22 = fields.Char(size=250, string="Champ 22")
    data_23 = fields.Char(size=250, string="Champ 23")
    data_24 = fields.Char(size=250, string="Champ 24")
    data_25 = fields.Char(size=250, string="Champ 25")
    data_26 = fields.Char(size=250, string="Champ 26")
    data_27 = fields.Char(size=250, string="Champ 27")
    data_28 = fields.Char(size=250, string="Champ 28")
    data_29 = fields.Char(size=250, string="Champ 29")
    data_30 = fields.Char(size=250, string="Champ 30")

    state = fields.Selection([("created", "Créé, non traité"),
                              ("processed", "Traité avec succès"),
                              ("error", "En erreur")],
                             required=True, default="created", string="Statut")

    retry_count = fields.Integer(default=0, required=True, string="Nombre d'exécutions",
                                 help="Nombre de tentatives d'exécution du flux.")
    cr_ids = fields.One2many(
        "dataexchange.stream.cr", "data_id", string="Compte-rendus")

    def addLogSuccess(self, message):
        _logger.info(message)
        self.env['dataexchange.stream.cr'].create({'message': message,
                                                   'data_id': self.id})

    def addLogError(self, message, code):
        _logger.warning("Code [" + code + "] :" + message)
        self.env['dataexchange.stream.cr'].create({'error_code': code,
                                                   'message': message,
                                                   'data_id': self.id})

    def addLogInfo(self, message):
        _logger.debug(message)
        self.env['dataexchange.stream.cr'].create({'message': message,
                                                   'data_id': self.id})


class StreamCR(models.Model):
    _name = "dataexchange.stream.cr"
    _description = "Compte-rendus"

    run_id = fields.Many2one(
        comodel_name="dataexchange.stream.run",
        ondelete="cascade",
        string="Exécution")

    message = fields.Text(
        size=100,
        string="Explication")

    data_id = fields.Many2one(
        comodel_name="dataexchange.stream.data",
        required=False,
        string="Enregistrement de données")

    is_error = fields.Boolean(
        compute='_is_error',
        store=True,
        string="Erreur")

    error_code = fields.Char(
        size=2,
        string="Code d'erreur")

    date_event = fields.Datetime(
        string="Date/Heure", default=fields.Datetime.now)

    @api.depends('error_code')
    def _is_error(self):
        for r in self:
            r.is_error = r.error_code
