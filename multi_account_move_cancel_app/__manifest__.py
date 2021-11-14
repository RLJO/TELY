# -*- coding: utf-8 -*-
{
    "name" : "Odoo Mass Journal Entry Cancel and Reset App",
    "author": "Edge Technologies",
    "version" : "12.0.1.0",
    "live_test_url":'https://youtu.be/kyVrQ9MglYo',
    "images":["static/description/main_screenshot.png"],
    'summary': 'Multiple Journal Entry Cancel reset journal entry cancel mass journal entries cancel journal entry reset journal entry reset to draft journal entries cancel multiple journal entries cancel and reset journal entry reverse mass journal entry reset to draft',
    "description": """
        Odoo Multiple Journal Entry Cancel App
    """,
    "license" : "OPL-1",
    "depends" : ['base','account'],
    "data": [
        'security/account_security.xml',
        'wizard/account_move_cancel_views.xml',
        'wizard/account_move_draft_views.xml',
        'views/account_view.xml',
    ],
    "auto_install": False,
    "installable": True,
    "price": 10,
    "currency": 'EUR',
    "category" : "Accounting",
    
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

