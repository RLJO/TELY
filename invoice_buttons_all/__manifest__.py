# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'To draft and to cancel selected all invoices in tree view',
    'version': '1.1',
    'website': '',
    
    "price": 12.00,
    "currency": 'USD',
    'license': 'AGPL-3',
    'author': 'Tb25',
    'email': 'torbatj79@gmail.com',
    
    'category': 'Invoice',
    'sequence': 1,
    'summary': 'To draft and to cancel all selected invoices',
    'depends': [
        'account',
        'account_cancel',
    ],
    'description': "One click draft or cancel all selected Invoices",
    'data': [
        'wizard/buttons_all_view.xml',
    ],
    'js': [
        
           ],
    'images': [
        'static/src/img/banner.png'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
