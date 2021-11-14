# -*- coding: utf-8 -*-

{
    'name': 'Multiple Invoice Payments',
    'version': '12.0.1.3',
    'category': 'account',
    'author': 'APPSGATE FZC LLC',
    'website': "http://www.apps-gate.net",
    
    'summary': 'Payment of multiple invoices in one screen',
    'description': """ 
            Pay multiple invoice
            Pay multiple Vendor bill
	   
		Multiple invoice payment, 
		Invocie Multiple payment,
	 	Payment,
		Partial Invocie Payment,
		Full invoice Payment,
		Payment Invoice,
	
		Multiple Vendor Bill Payment,
		Multiple Credit note payment,
		
		
		multi payment,
		multiple payment,
     """,

    'depends': ['account'],
    
    'data': [
           'views/account_payment_inehrit.xml',
           'security/ir.model.access.csv',
             ],

    'images': [
        'static/src/img/main-screenshot.png'
    ],
   # "images":[''],
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
    
    'currency': 'USD',
    'price': 15.00,
    
}

