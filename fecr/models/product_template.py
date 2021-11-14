from odoo import api, fields, models


class ProductElectronic(models.Model):
    _inherit = "product.template"

    @api.model
    def _default_code_type_id(self):
        code_type_id = self.env["code.type.product"].search([("code", "=", "04")], limit=1)
        return code_type_id or False

    commercial_measurement = fields.Char(  # TODO necessary?
        string="Commercial Measurement Unit",
        required=False,
    )
    code_type_id = fields.Many2one(  # TODO Is this necessary?
        comodel_name="code.type.product",
        required=False,
        default=_default_code_type_id,
    )
    tariff_head = fields.Char(
        string="Tariff item for export invoice",
        required=False,
    )
    cabys_id = fields.Many2one(
        string="CAByS",
        comodel_name="cabys",
        ondelete="restrict",
        required=False,  # TODO required?
    )
    taxes_id = fields.Many2many(
        compute="_compute_tax_from_cabys",
        store=True,
    )

    @api.depends("cabys_id")
    def _compute_tax_from_cabys(
        self,
    ):  # TODO the change doesn't occur in real time in the frontend
        for template in self:
            if not template.cabys_id:
                continue
            template.taxes_id = [(6, None, [template.cabys_id.tax_id.id])]
