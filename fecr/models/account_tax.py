import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class IvaCodeType(models.Model):
    _inherit = "account.tax"

    tax_code = fields.Char(
        required=False,
    )
    iva_tax_desc = fields.Char(
        string="VAT rate",
        default="N/A",
        required=False,
    )
    iva_tax_code = fields.Char(
        string="VAT Rate Code",
        default="N/A",
        required=False,
    )
    has_exoneration = fields.Boolean(
        string="Tax Exonerated",
        required=False,
    )
    percentage_exoneration = fields.Integer()
    tax_root = fields.Many2one(
        comodel_name="account.tax",
        required=False,
    )

    @api.onchange("percentage_exoneration")
    def _onchange_percentage_exoneration(self):
        self.tax_compute_exoneration()

    @api.onchange("tax_root")
    def _onchange_tax_root(self):
        self.tax_compute_exoneration()

    def tax_compute_exoneration(self):
        if self.percentage_exoneration <= 100:
            if self.tax_root:
                _tax_amount = self.tax_root.amount / 100
                _procentage = self.percentage_exoneration / 100
                self.amount = (_tax_amount * (1 - _procentage)) * 100
        else:
            raise UserError(_("The percentage cannot be greater than 100"))
