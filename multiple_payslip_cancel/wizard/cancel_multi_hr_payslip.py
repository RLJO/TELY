from odoo import api, models


class CancelMultiPayslip(models.TransientModel):
    _name = "cancel.multi.hr.payslip"
    _description = "Cancel Multi Payslip"

    @api.multi
    def action_cancel(self):
        payslips = self.env.context.get('active_ids')
        cancel_payslips = self.env['hr.payslip'].browse(payslips)
        res = True
        for payslip in cancel_payslips:
            res = payslip.action_payslip_cancel()
        return res