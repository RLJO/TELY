from odoo import fields, models


class PaymentMethods(models.Model):
    _name = "payment.methods"
    _description = "Payment Method"

    active = fields.Boolean(
        required=False,
        default=True,
    )
    sequence = fields.Char(
        required=False,
    )
    name = fields.Char(
        required=False,
    )
    notes = fields.Text(
        required=False,
    )
