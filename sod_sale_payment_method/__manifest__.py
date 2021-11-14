# -*- coding: utf-8 -*-
# Copyright 2018 Sodexis
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': "Sale Payment Method ",
    'summary': """This modules helps to add payment method on the Customer and the Sale Order. """,
    'version': '12.0.1.0.0',
    'category': 'Sale',
    'website': "http://sodexis.com/",
    'author': "Sodexis, Inc <dev@sodexis.com>",
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'depends': [
        'account',
        'sale',
    ],
    'data': [
        'views/res_partner_view.xml',
        'views/sale_view.xml',
    ],
}
