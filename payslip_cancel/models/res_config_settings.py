# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    cancel_payslip = fields.Boolean(string="Cancel Done Payslip?")

    @api.multi
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            cancel_payslip=self.env.user.company_id.cancel_payslip ,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        company_id = self.env.user.company_id
        company_id.cancel_payslip = self.cancel_payslip