# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Cancel Multiple Payslips',
    'version' : '1.0',
    'author':'Craftsync Technologies',
    'category': 'stock',
    'maintainer': 'Craftsync Technologies',
    'summary': "Enable mass cancel employee's payslip workflow. Even if payslip was validated. Now user can select multi payslips for cancel",
    'website': 'https://www.craftsync.com/',
    'license': 'OPL-1',
    'support':'info@craftsync.com',
    'depends' : ['payslip_cancel'],
    'data': [
	   'views/view_cancel_payslip.xml',
    ],    
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/main_screen.png'],
    'price': 5.00,
    'currency': 'EUR',

}
