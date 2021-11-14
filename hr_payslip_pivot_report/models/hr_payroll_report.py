# -*- coding: utf-8 -*-
#################################################################################
# Author      : Kanak Infosystems LLP. (<http://kanakinfosystems.com/>)
# Copyright(c): 2012-Present Kanak Infosystems LLP.
# All Rights Reserved.
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <http://kanakinfosystems.com/license>
#################################################################################

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import fields, models, tools, api

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    total_net = fields.Float(string='Total Net Salary', compute='_salary_computation', store=True)
    total_base_salary = fields.Float(string='Total Base Salary', compute='_salary_computation', store=True)
    total_allowance = fields.Float(string='Total Allowance', compute='_salary_computation', store=True)
    total_deductions = fields.Float(string='Total Deductions', compute='_salary_computation', store=True)

    @api.multi
    @api.depends('line_ids.total')
    def _salary_computation(self):
        for l in self:
            l.total_net = sum(l.line_ids.filtered(lambda l: l.category_id.code == 'NET').mapped('total'))
            l.total_base_salary = sum(l.line_ids.filtered(lambda l: l.category_id.code == 'BASIC').mapped('total'))
            l.total_allowance = sum(l.line_ids.filtered(lambda l: l.category_id.code == 'ALW').mapped('total'))
            l.total_deductions = sum(l.line_ids.filtered(lambda l: l.category_id.code == 'DED').mapped('total'))

class PayrollReportView(models.Model):
    _name = 'hr.payroll.report.view'
    _auto = False

    name = fields.Many2one('hr.employee', string='Employee')
    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')
    state = fields.Selection([('draft', 'Draft'), ('verify', 'Waiting'), ('done', 'Done'), ('cancel', 'Rejected')],
                             string='Status')
    job_id = fields.Many2one('hr.job', string='Job Title')
    company_id = fields.Many2one('res.company', string='Company')
    department_id = fields.Many2one('hr.department', string='Department')
    total_net = fields.Float(string='Net Salary')
    total_base_salary = fields.Float(string='Base Salary')
    total_allowance = fields.Float(string='Allowance')
    total_deductions = fields.Float(string='Deductions')
    leaves_count = fields.Float(string='Leaves')
    # category_id = fields.Many2one('hr.salary.rule.category', string='Salary Rule Category')
    # salary_rule_id = fields.Many2one('hr.salary.rule', string='Salary Rule')

    def _select(self):
        select_str = """
        min(ps.id) as id,emp.id as name,jb.id as job_id,
        dp.id as department_id,cmp.id as company_id,
        hl.number_of_days as leaves_count,
        ps.date_from, ps.date_to, ps.total_net as total_net, ps.state as state, ps.total_base_salary as total_base_salary, ps.total_allowance as total_allowance, ps.total_deductions as total_deductions
        """
        return select_str

    def _from(self):
        from_str = """
            hr_payslip_line psl
                join hr_payslip ps on (ps.employee_id=psl.employee_id and ps.id=psl.slip_id)
                    left join hr_leave hl on (ps.employee_id=hl.employee_id)
                join hr_employee emp on (ps.employee_id=emp.id)
                join hr_department dp on (emp.department_id=dp.id)
                join hr_job jb on (emp.job_id=jb.id)join res_company cmp on (cmp.id=ps.company_id)
         """
        return from_str

    def _group_by(self):
        group_by_str = """
            group by hl.number_of_days,emp.id,ps.date_from, ps.date_to, ps.state,jb.id,dp.id,cmp.id,ps.total_net,ps.total_base_salary,ps.total_allowance,ps.total_deductions
        """
        return group_by_str

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as ( SELECT
               %s
               FROM %s
               %s
               )""" % (self._table, self._select(), self._from(), self._group_by()))


