import logging

from odoo import api, models
from odoo.tools import convert_file

_logger = logging.getLogger(__name__)

MODULE_NAME = "fecr"


class Tool(models.AbstractModel):
    _name = "tool"
    _description = "Tool"

    @api.model
    def load_csv(self, filename, cr):
        _logger.info("Loading {} file".format(filename))
        convert_file(
            cr=cr,
            module=MODULE_NAME,
            filename=filename,
            idref=None,
            mode="init",
            noupdate=True,
        )
