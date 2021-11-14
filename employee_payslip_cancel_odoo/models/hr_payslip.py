# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import ValidationError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_reset_payslip_custom(self):
        if any(slip.state != 'done' for slip in self):
            raise ValidationError("Cannot Reset a payslip(s) that is not done.")
        self.write({
            'state': 'cancel',
        })
        self.with_context(force_delete=True).action_payslip_cancel()
        self.write({
            'state': 'draft',
            'date': False,
        })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
