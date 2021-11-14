from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime

class Picking_inherit(models.Model):
    _inherit = "stock.picking"


    sale_state = fields.Selection([
        ('draft', 'Quotation'),
        ('to_be_approved','Approved'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3, related="sale_id.state")
        

    

    show_approve = fields.Boolean(string="Show Approve",related='sale_id.show_approve')

    
    



    def action_see_approve(self):
    	return

