# -*- coding: utf-8 -*-
from odoo import models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def get_customer_invoice_template_id(self):
        self.ensure_one()
        if self.type != 'out_invoice':
            return False
        return self.env['reporting.custom.template'].sudo().get_template('report_customer_invoice')
