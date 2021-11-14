# -*- coding: utf-8 -*-
{
    'name': "CRM Multi Currencies",

    'summary': """
        Manage multi currencies in CRM
		""",

    'description': """
        Manage multi currencies in CRM
    """,

    'author': "DarbTech",
    'website': "https://darbtech.net",
	'support': 'support@darbtech.net',
	
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '12.0.0.1',
	'price': 49.99,
    'currency': 'EUR',
	'license': 'Other proprietary',
    'images': ['static/crm_multi_currencies_dt.png'],	
    # any module necessary for this one to work correctly
    'depends': ['base', 'crm'
                ],

    # always loaded
    'data': [
        'views/partner.xml',
        'views/crm.xml',
    ],

    'qweb': [
        'static/src/xml/*.xml',
    ],

    # only loaded in demonstration mode
    'demo': [
    ],
}
