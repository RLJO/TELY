import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class CodeTypeProduct(models.Model):
    _name = "code.type.product"
    _description = "Code Type Product"

    code = fields.Char(
        required=False,
    )
    name = fields.Char(
        required=False,
    )
