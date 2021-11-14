# -*- coding: utf-8 -*-
# Copyright 2018 Openinside co. W.L.L.
{
    "name": "Pay Employee Expense In Payroll",
    "summary": "Pay Employee Expense In Payroll, Reimburse, Reimbursed, Reimbursement, Employee Expense, Employee's Expense, HR Expenses, Payroll, Payroll Integration, Salary Rule, Payslip, Pay Slip, Employee Payslip, Expense Reimburse",
    "version": "12.0.1.1.0",
    'category': 'Human Resources',
    "website": "https://www.open-inside.com",
	"description": """
		 Payroll Expenses Reimbursements
		 
    """,
	'images':[
        'static/description/cover.png'
	],
    "author": "Openinside",
    "license": "OPL-1",
    "price" : 29.99,
    "currency": 'EUR',
    "installable": True,
    "depends": [
        'hr_payroll','hr_payroll_account', 'hr_expense'
    ],
    "data": [
        'data/hr_salary_rule.xml',
        'view/hr_expense_sheet.xml'
    ],
    'odoo-apps' : True    
}

