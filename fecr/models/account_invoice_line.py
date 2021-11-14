from odoo import api, fields, models


class InvoiceLineElectronic(models.Model):
    _inherit = "account.invoice.line"

    total_amount = fields.Float(
        required=False,
    )
    discount_note = fields.Char(
        required=False,
    )
    total_tax = fields.Float(
        compute="_compute_total_tax",
        store=True,
    )
    third_party_id = fields.Many2one(
        comodel_name="res.partner",
    )
    tariff_head = fields.Char(
        string="Tariff heading for export invoice",
        required=False,
    )
    categ_name = fields.Char(
        related="product_id.categ_id.name",
    )
    product_code = fields.Char(
        related="product_id.default_code",
    )
    no_discount_amount = fields.Monetary(
        compute="_compute_discount_amount",
    )
    discount_amount = fields.Monetary(
        compute="_compute_discount_amount",
    )
    price_subtotal_incl = fields.Monetary(
        compute="_compute_price_subtotal_incl",
    )

    @api.depends("quantity", "price_unit", "discount")
    def _compute_discount_amount(self):
        for record in self:
            record.no_discount_amount = record.quantity * record.price_unit
            record.discount_amount = record.no_discount_amount * record.discount / 100

    @api.depends("invoice_line_tax_ids", "price_subtotal")
    def _compute_total_tax(self):
        for line in self:
            line.total_tax = sum(
                line.invoice_line_tax_ids.mapped(lambda tax: tax.amount / 100 * line.price_subtotal)
            )

    @api.depends("price_subtotal", "total_tax")
    def _compute_price_subtotal_incl(self):
        for line in self:
            line.price_subtotal_incl = line.price_subtotal + line.total_tax
