# -*- coding: utf-8 -*-

{
    "name" : "Import Customer Invoice and Vendor Bill",
    "author": "Edge Technologies",
    "version" : "12.0.1.4",
    "live_test_url":'https://youtu.be/roRWFEah8Sw',
    "images":['static/description/main_screenshot.png'],
    'summary': 'This app is helpful for easy to import multiple invoice / Bill from csv and excel file.',
    "description": """
    
   This app is helpful for easy to import multiple invoice / Bill from csv and excel file. import invoice import bills import vendor bills import bills
add invoices 
import inovoices from excel import inovoices from csv , supplier invoice lines , vendor bills  import refund import credit note import invoice with analytic account import analytic invoice  invoice by csv add invoices by excel invoice from excel import customer invoices 
    import Sale Order From Excel Import Invoice Lines From Excel Import Invoice Lines from CSV/Excel file Import Invoice/Bill Lines from CSV/Excel file Account Invoice Import invoices Import from Excel bill import from excel  bills import from excel bil reciept import import bill reciept

    """,
    "license" : "OPL-1",
    "depends" : ['base','stock','sale_management','purchase','account'],
    "data": [
        'wizard/import_wizard.xml',
        'wizard/validation.xml',
        'views/invoice_inherit.xml',
    ],
    "auto_install": False,
    "installable": True,
    "price": 15,
    "currency": 'EUR',
    "category" : "Accounting",
    
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
