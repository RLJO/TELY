from odoo import fields, models


class Resolution(models.Model):
    _name = "resolution"
    _description = "Resolution"

    active = fields.Boolean(
        required=False,
        default=True,
    )
    name = fields.Char(
        required=False,
    )
    date_resolution = fields.Date(
        required=False,
    )
