from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoice_import_ids = fields.One2many(
        comodel_name="account.invoice.import.config",
        inverse_name="partner_id",
        string="Invoice Import Configuration",
    )
    invoice_import_count = fields.Integer(
        compute="_compute_invoice_import_count",
        string="Number of Invoice Import Configurations",
        readonly=True,
    )

    def _compute_invoice_import_count(self):
        config_data = self.env["account.invoice.import.config"].read_group(
            [("partner_id", "in", self.ids)], ["partner_id"], ["partner_id"]
        )
        mapped_data = {
            config["partner_id"][0]: config["partner_id_count"] for config in config_data
        }

        for partner in self:
            partner.invoice_import_count = mapped_data.get(partner.id, 0)
