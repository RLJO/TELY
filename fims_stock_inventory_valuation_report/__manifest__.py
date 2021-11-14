# -*- coding: utf-8 -*-
###############################################################################
#
# Fortutech IMS Pvt. Ltd.
# Copyright (C) 2016-TODAY Fortutech IMS Pvt. Ltd.(<http://www.fortutechims.com>).
#
###############################################################################
{
    'name': 'Stock Inventory Valuation Report',
    'category': 'stock',
    'summary': 'This module allow you to check real time stock information base on different location',
    'version': '12.0.0',
    'license': 'OPL-1',
    'description': """This module will allow to cancel Website Sale Portal Quotation and Order""",
    'depends': ['sale', 'stock', 'purchase'],
    'author': 'Fortutech IMS Pvt. Ltd.',
    'website': 'https://www.fortutechims.com',
    'data': [
        'views/stock_valuation.xml',
        'report/stock_valuation_report.xml',
    ],
    "price":49.0,
    "currency":"EUR",
    "installable": True,
    "application": True,
    "auto_install": False,
    "images":['static/description/banner.png'],
}
