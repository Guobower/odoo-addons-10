# -*- coding: utf-8 -*-
# © 2018  e-COSI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
import logging
from odoo import http

_logger = logging.getLogger(__name__)

db_filter_org = http.db_filter


def db_filter(dbs, httprequest=None):
    httprequest = httprequest or http.request.httprequest

    db_filter_hdr_before = httprequest.environ.get(
        'HTTP_X_ODOO_DBFILTER_BEFORE')
    db_filter_hdr_after = httprequest.environ.get('HTTP_X_ODOO_DBFILTER_AFTER')
    db_filter_hdr_only = httprequest.environ.get('HTTP_X_ODOO_DBFILTER_ONLY')

    if db_filter_hdr_only:
        dbs = [db for db in dbs if re.match(db_filter_hdr_only, db)]
        _logger.debug('Header DB Filter only : %s', db_filter_hdr_only)
    elif db_filter_hdr_before:
        dbs = [db for db in dbs if re.match(db_filter_hdr_before, db)]
        dbs = db_filter_org(dbs, httprequest)
        _logger.debug('Header DB Filter before : %s', db_filter_hdr_before)
    elif db_filter_hdr_after:
        dbs = db_filter_org(dbs, httprequest)
        dbs = [db for db in dbs if re.match(db_filter_hdr_after, db)]
        _logger.debug('Header DB Filter after : %s', db_filter_hdr_after)

    if not dbs:
        dbs = db_filter_org(dbs, httprequest)

    return dbs


http.db_filter = db_filter
