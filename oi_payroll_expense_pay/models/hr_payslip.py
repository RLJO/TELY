'''
Created on Oct 22, 2018

@author: Zuhair Hammadi
'''
from odoo import models, api
from collections import defaultdict

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    @api.multi
    def action_payslip_done(self):  
        res = super(HrPayslip, self).action_payslip_done()
        for record in self:
            sheet_ids = self.env['hr.expense.sheet'].search([('payslip_id', '=', record.id)])
            if sheet_ids:
                vals = defaultdict(lambda : self.env['account.move.line'])
                for line in sheet_ids.mapped('account_move_id.line_ids'):
                    if line.account_id.user_type_id.type == 'payable':   
                        vals[line.account_id] += line
                for account_id, expense_line_ids in vals.items():
                    slip_line_ids = self.env['account.move.line']
                    for line in record.mapped('move_id.line_ids'):
                        if line.account_id == account_id:
                            slip_line_ids += line
                    (expense_line_ids + slip_line_ids).reconcile()                
        return res