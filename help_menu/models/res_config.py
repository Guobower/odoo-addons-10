from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class BaseConfigSettings(models.TransientModel):
    _name = "help_menu.settings"
    _inherit = "res.config.settings"

    help_url = fields.Text(string="Online help URL")

    # Gets URL value from the action (for config page)
    @api.model
    def get_values(self):
        res = super(BaseConfigSettings, self).get_values()
        res.update(
            help_url=self.env.ref("help_menu.url_action").url
        )
        return res

    # Sets the new URL value (for config page)
    @api.multi
    def set_values(self):
        self.env.ref("help_menu.url_action").write({
            "url": self.help_url,
        })
        _logger.debug("Help Menu - New URL set.")
