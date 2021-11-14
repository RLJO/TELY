'''
Created on Mar 3, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields

class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"
    
    payslip_id = fields.Many2one('hr.payslip', readonly = True, ondelete = 'set null')
    