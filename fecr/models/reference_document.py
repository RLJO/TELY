from odoo import fields, models


class ReferenceDocument(models.Model):
    _name = "reference.document"
    _description = "Reference Document"

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
