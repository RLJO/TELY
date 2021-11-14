from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice.tax"

    type = fields.Selection(
        related="invoice_id.type",
        store=True,
    )
    purchase_type = fields.Selection(
        related="invoice_id.purchase_type",
        store=True,
    )
    type_tax_use = fields.Selection(
        related="tax_id.type_tax_use",
        store=True,
    )
    activity_id = fields.Many2one(
        related="invoice_id.activity_id",
        store=True,
    )
    amount_sale = fields.Monetary(
        compute="_compute_amount_sale",
        store=True,
    )
    date_invoice = fields.Date(
        related="invoice_id.date_invoice",
    )
    state = fields.Selection(
        related="invoice_id.state",
    )

    @api.depends("amount_total", "base")
    def _compute_amount_sale(self):
        for record in self:
            record.amount_sale = record.base + record.amount_total
