# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Payslip Reset to Draft After Done',
    'price': 49.0,
    'version': '1.1.3',
    'depends': [
       'hr_payroll',
       'hr_payroll_account',
    ],
    'currency': 'EUR',
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    # 'live_test_url': 'https://youtu.be/sYKloqpIJvQ',
    'live_test_url' : 'https://youtu.be/qEuhsDghCP0',
    'data':[
        'views/hr_payslip_view.xml',
        'wizard/employee_payslip_cancel_view.xml',
    ],
    'category': 'Human Resources/Payroll',
    'license': 'Other proprietary',
    'summary': """Allow to reset to draft payslip after payslip done.""",
    'description': """
This app allow manager reset to draft payslip after payslip done,
Allow user to Reset Employee Payslip
After Reset/Cancel Payslip journal entry will be removed
After Reset/Cancel allow User to Re-edit the payslip details

    """,
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
