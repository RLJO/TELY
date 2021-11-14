import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class IdentificationType(models.Model):
    _name = "identification.type"
    _description = "Identification Type"

    code = fields.Char(
        required=False,
    )
    name = fields.Char(
        required=False,
    )
    notes = fields.Text(
        required=False,
    )
