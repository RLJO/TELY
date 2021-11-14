# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name" : "Import bank statement lines from CSV/Excel file",
    "author" : "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",    
    "category": "Accounting",
    "summary": "Import Bank Statement Lines From CSV Module, Import Bank Statement Lines From Excel App, import Bank Statement Lines From XLS, import Bank Statement Lines From XLSX Odoo",
    "description": """This module is useful to import bank statement lines from CSV/Excel. You can import custom fields from CSV or Excel.""",     
    "version":"12.0.3",
    "depends" : ["base","account","sh_message",],
    "application" : True,
    "data" : [
        
            "security/import_bsl_security.xml",
            "wizard/import_bsl_wizard.xml",
            "views/account_view.xml",
            
            ],         
    "external_dependencies" : {
        "python" : ["xlrd"],
    },                  
    "images": ["static/description/background.png",],   
    "live_test_url": "https://youtu.be/LNi1bj51FUU",           
    "auto_install":False,
    "installable" : True,
    "price": 15,
    "currency": "EUR"   
}
