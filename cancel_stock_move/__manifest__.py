# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
{
    'name' : 'Cancel Stock Move',
    'version' : '1.0',
    'author':'Craftsync Technologies',
    'category': 'Manufacturing',
    'maintainer': 'Craftsync Technologies',
    'description': """

        You can cancel MO with company wise configuration

    """,
    'summary': """
            cancel confirmed move cancel confirmed stock move cancel confirmed moves cancel confirmed stock moves

cancel processed move cancel processed stock move cancel processed moves cancel processed stock moves

cancel done move cancel done stock move cancel done stock moves cancel done moves

cancel transferred move cancel transferred stock move cancel transferred moves cancel transferred stock moves

Cancel completed move Cancel completed moves Cancel completed stock move Cancel completed stock moves

Reset to draft move Reset to draft moves Reset to draft stock move Reset to draft stock moves

reset to draft move reset to draft moves reset to draft stock move reset to draft stock moves

cancel move transaction cancel stock move transaction cancel Move cancel stock moves transaction cancel moves transaction

cancel stock Cancel inventory cancel sale cancel purchase Cancel picking Cancel incoming shipment

cancel Stock cancel Inventory Cancel Stock Cancel Inventory Cancel sales cancel purchase cancel picking cancel incoming shipment

cancel stock cancel inventory cancel sales cancel purchases cancel pickings cancel incoming shipments cancel delivery

cancel inventory moves cancel inventory move cancel stock moves cancel stock move

Cancel Inventory Moves Cancel Inventory Move Cancel Stock Moves Cancel Stock Move
    """,


    'website': 'https://www.craftsync.com/',
    'license': 'OPL-1',
    'support':'info@craftsync.com',
    'depends' : ['stock','account_cancel'],
    'data': [
        'views/res_config_settings_views.xml',
	    'views/view_stock_move.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/main_screen.png'], 
    'price': 19.99,
    'currency': 'EUR',
}
