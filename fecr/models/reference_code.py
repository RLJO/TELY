from odoo import fields, models


class ReferenceCode(models.Model):
    _name = "reference.code"
    _description = "Reference Code"

    active = fields.Boolean(
        required=False,
        default=True,
    )
    code = fields.Char(
        required=False,
    )
    name = fields.Char(
        required=False,
    )
