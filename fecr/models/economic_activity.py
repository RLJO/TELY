from odoo import fields, models


class EconomicActivity(models.Model):
    _name = "economic_activity"
    _description = "Economic Activity"
    _order = ""

    active = fields.Boolean(
        default=True,
    )
    code = fields.Char(
        required=False,  # TODO check
    )
    name = fields.Char(
        required=False,  # TODO check
    )
    description = fields.Char(
        required=False,  # TODO check
    )
