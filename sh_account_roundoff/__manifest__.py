# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Account Round Off",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "version": "12.0.1",
    "category": "Accounting",
    "summary": "Amount Round Off, Invoice rounding, Account Amount round Off, Invoice Round Off, Bill Round Off, Credit Note Round Off, Debite Note Round Off, Payment Round Off, Payments Round Off Odoo",
    "description": """Cash rounding is required at some times. This module automatically rounds the total amount in the invoices/ bills/ credit notes/ debit notes. You can also create a separate journal entry for the rounded amount. """,
    "depends": [
        'account'
    ],
    "data": [
        "views/res_config_setting.xml",
        "views/invoice_view.xml",
    ],
    "images": ["static/description/background.png", ],
    "license": "OPL-1",
    "installable": True,
    "auto_install": False,
    "application": True,
    "price": 15,
    "currency": "EUR"
}
