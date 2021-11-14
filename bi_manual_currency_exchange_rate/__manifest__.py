# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    "name" : "Currency Exchange Rate on Invoice/Payment/Sale/Purchase in Odoo",
    "version" : "12.0.1.5",
    "depends" : ['base','account','purchase','sale_management','stock'],
    "author": "BrowseInfo",
    "summary": "This module helps to apply manual currency rate on invoice, payment, sales and purchase order ",
    "description": """
    Odoo/OpenERP module for manul currency rate converter
    Currency Exchange Rate on Invoice/Payment/Sale/Purchase, manual multi currency process on invoice, multi currency payment
    Currency Exchange Rate on Payment/Sale/Purchase
    Manual Currency Exchange Rate on invoice payment
    Manual Currency Rate on invoice payment
    Currency Exchange Rate on Sales order
    Currency Exchange Rate on Sale order
    Currency Exchange Rate on Purchase Order
    Apply Manual Currency Exchange Rate on Invoice/Payment/Sale/Purchase
    Apply Manual Currency Exchange Rate on Payment
    Apply Manual Currency Exchange Rate on Sale Order
    Apply Manual Currency Exchange Rate on Purchase OrderCurrency Exchange Rate on Sale/Purchase
    Currency Exchange Rate on Sales order
    Currency Exchange Rate on Purchase Order
    Apply Manual Currency Exchange Rate on Sale/Purchase
    Apply Manual Currency Exchange Rate on Sale Order
	Currency Exchange Rate on Invoice/Payment, manual multi currency process on invoice, multi currency payment
    Currency Exchange Rate on Payment
    Manual Currency Exchange Rate on invoice payment , Currency Exchange Rate for invoice , Currency Exchange Rate in invoice , invoice Currency Exchange Rate , invoice
    Manual Currency Rate on invoice payment Exchange Rate on 
    Apply Manual Currency Exchange Rate on Invoice/Payment
    Apply Manual Currency Exchange Rate on Payment
	add Manual Currency Exchange Rate
	multiple currency rate , many currency 
    Exchange Currency rate
    custom exchange rate
    Rates of Exchange 
    Exchange Rates
    custom exchange rate
    Customs Exchange Rate
    Conversion rates
    dollar exchange rate
    real exchange rate
    Currency Exchange Rate Update
    Currency Rate Update
    Currency Rates Update
    multi-currency rates
    multicurrency exchanges rates
    exchange rate
    exchange rates

    Apply Manual Currency Rate on Invoice/Payment
    Apply Manual Currency Rate on Payment
    multi-currency process on invoice, multi-currency payment
    currency converter on Odoo
    invoice currency rate
    Manual Exchange rate of Currency apply
    manual currency rate on invoice
    currency rate apply manually
    Apply Manual Currency Exchange Rate on Purchase Order

    Apply Manual Currency Rate on Sale/Purchase
    Apply Manual Currency Rate on Sale Order
    Apply Manual Currency Rate on Purchase Order
    multi-currency process on invoice, multi-currency payment
    currency converter on Odoo
    invoice currency rate

    Apply Manual Currency Rate on Invoice/Payment/Sale/Purchase
    Apply Manual Currency Rate on Payment
    Apply Manual Currency Rate on Sale Order
    Apply Manual Currency Rate on Purchase Order
    multi-currency process on invoice, multi-currency payment
    currency converter on Odoo
    invoice currency rate
    Manual Exchange rate of Currency apply
    manual currency rate on invoice
    currency rate apply manually

    """,
    "price": 18,
    "currency": "EUR",
    'category': 'Accounting',
    "website" : "https://www.browseinfo.in",
    "data" :[
             "views/customer_invoice.xml",
             "views/account_payment_view.xml",
             "views/purchase_view.xml",
             "views/sale_view.xml",
    ],
    'qweb':[
    ],
    "auto_install": False,
    "installable": True,
    'live_test_url':'https://youtu.be/nRdIuuxi9yI',
	"images":['static/description/Banner.png'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
