from odoo import fields, models


class AutEx(models.Model):
    _name = "aut.ex"
    _description = "Autorization Model"

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
