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

{
    'name': 'Payslip Report (Payroll)',
    'version': '1.0',
    'summary': 'Month wise, employee wise payroll report which can be exported to excel as well',
    'description': """Payslip Report (Payroll).
    This module gives a pivot view for the HR managers. they can see all the 'NET', 'BASIC', 'Allowances' and Deductions amount and Leaves of payslips in all states""",
    'author': 'Kanak Infosystems LLP.',
    'company': 'Kanak Infosystems LLP.',
    'maintainer': 'Kanak Infosystems LLP.',
    'website': 'http://www.kanakinfosystems.com',
    'category': 'Generic Modules/Human Resources',
    'depends': ['hr_payroll'],
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/menu_payslip_report.xml'
    ],
    'demo': [],
    'images': ['static/description/banner.jpg'],
    'application': True,
    'price': 30,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
}
