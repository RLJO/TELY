# -*- coding: utf-8 -*-

{
    'name': 'Customer/Vendor Loan',
    'version' : '1.0',
    'author':'Craftsync Technologies',
    'maintainer': 'Craftsync Technologies',
    "license": "OPL-1",
    'summary': "Manage Customer and Supplier Loan",
    'website': 'https://www.craftsync.com',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/amount_pay.xml',
        'views/full_payment.xml',
        'views/loan_view.xml',
        'views/res_config_settings_views.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'price': 29.99,
    'currency': 'EUR',
    'images': ['static/description/main_screen.png'],
    'external_dependencies': {
        'python': [
            'numpy',
        ],}
}
