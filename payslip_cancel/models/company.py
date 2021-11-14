from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    cancel_payslip = fields.Boolean(string="Cancel Done Payslip?")
