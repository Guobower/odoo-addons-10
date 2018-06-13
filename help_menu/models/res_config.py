from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class BaseConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    _name = "help_menu.settings"

    help_url = fields.Text(string="Online help URL")

    # Gets URL value from the action (for config page)
    @api.model
    def get_default_help_url(self, fields):
        action = self.env.ref("help_menu.url_action")
        return {
            "help_url": action.url
        }

    # Sets the new URL value (for config page)
    @api.model
    def set_help_url(self):
        self.env.ref("help_menu.url_action").write({
            "url": self.help_url,
        })
        _logger.debug("Help Menu - New URL set.")

