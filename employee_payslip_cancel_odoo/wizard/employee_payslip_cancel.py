# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PayslipCancel(models.TransientModel):
    _name = 'custom.employee.payslip.cancel'

    is_confirm_payslip_cancel = fields.Boolean(
        string="Are you sure do you want reset payslip to draft state?",
    )

    def action_reset_payslip_to_draft(self):
        if not self.is_confirm_payslip_cancel:
            raise ValidationError("You can not reset payslip to draft please confirm by checking box on wizard.")
        active_ids = self._context.get("active_ids")
        if active_ids:
            payslip_ids = self.env['hr.payslip'].browse(active_ids)
            payslip_ids.action_reset_payslip_custom()
            action = self.env.ref("hr_payroll.action_view_hr_payslip_form").read()[0]
            action['domain'] = [('id', 'in', active_ids)]
            return action
        return {}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
