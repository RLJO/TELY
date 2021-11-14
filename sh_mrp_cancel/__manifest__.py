# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

{
    "name": "Cancel MRP | Cancel Manufacturing Orders |Cancel Manufacturing | Cancel MRP Orders",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Manufacturing",
    "license": "OPL-1",
    "summary": "Cancel MRP Orders, Cancel Manufacturing Order,MRP Cancel,MRP Order Cancel, Manufacturing Orders Cancel, Cancel BOM, Cancel BIll Of Materials,Remove MRP Order, Delete MRP Order, Manufacturing Orders Delete, Delete Manufacturing Order Odoo",
    "description": """This module helps to cancel MRP(Manufacturing Orders). You can also cancel multiple MRP orders from the tree view. You can cancel the MRP orders in 3 ways,

1) Cancel Only: When you cancel the MRP order then the MRP order is canceled and the state is changed to "cancelled".
2) Cancel and Reset to Draft: When you cancel MRP order, first MRP order is canceled and then reset to the draft state.
3) Cancel and Delete: When you cancel the MRP order then first MRP order is canceled and then MRP order will be deleted.""",
    "version": "12.0.3",
    "depends": [
                "mrp",

    ],
    "application": True,
    "data": [
        'security/mrp_security.xml',
        'data/data.xml',
        'views/mrp_config_settings.xml',
        'views/views.xml',
    ],
    "images": ["static/description/background.png", ],
    "auto_install": False,
    "installable": True,
    "price": 20,
    "currency": "EUR"
}
