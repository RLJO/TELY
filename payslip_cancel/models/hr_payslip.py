from odoo import api, models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    def action_payslip_cancel(self):        
        flag = self.env['ir.model.fields'].search([('model','=','hr.payslip'),('name','=','move_id')])    
        for slip in self:

            if slip.company_id.cancel_payslip:
                if flag and slip.move_id:
                    if slip.move_id.journal_id:
                        slip.move_id.journal_id.update_posted = True
                    slip.move_id.button_cancel()
                    slip.move_id.unlink()
                slip.write({'state': 'cancel'})
                    
        return super(HrPayslip, self).action_payslip_cancel()