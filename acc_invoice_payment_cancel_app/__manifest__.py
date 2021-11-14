# -*- coding: utf-8 -*-
{
    'name': 'Cancel Invoice Cancel Account Payment',
    "author": "Edge Technologies",
    'version': '12.0.1.0',
    'live_test_url': "https://youtu.be/uOSKKPrAzPY",
    "images":['static/description/main_screenshot.png'],
    "summary" : 'Invoice Cancel Payment cancel journal entry cancel journal entries customer invoice cancel vendor bill cancel bill payment cancel invoicing cancel accounting payment cancel all in one account cancel delete invoice delete payment',
    'description': """ 
        Cancel Invoice | Cancel Payment
    """,
    "license" : "OPL-1",
    'depends': ['base','sale_management'],
    'data': [ 
        'security/security.xml',
        'views/account_move_action.xml',
        'views/account_payment_action.xml',
        'views/account_move.xml',
        'views/account_payment.xml',
        'views/res_company.xml',
        'views/res_config_settings.xml',      
            ],
    'installable': True,
    'auto_install': False,
    'price': 12,
    'currency': "EUR",
    'category': 'Accounting',

}

