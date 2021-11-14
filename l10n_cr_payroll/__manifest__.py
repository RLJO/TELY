# -*- coding: utf-8 -*-
{
    'name': "l10n_cr_payroll",

    'summary': """
       Mejorar campos que se crearon manualmente""",

    'description': """
        -
    """,

    'author': "Jhonny Mack Merino Samillan, Chiclayo-Perú",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_contract','hr_payroll'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_contract_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}