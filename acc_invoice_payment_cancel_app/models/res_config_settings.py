# -*- coding: utf-8 -*-
from odoo import models, fields, api,_

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    invoice_opration_type = fields.Selection([('cancel','Cancel'),('draft','Cancel and Set to Draft'),('delete','Cancel and Delete')],string='Invoice Opration Type', related="company_id.invoice_opration_type" ,readonly=False)
    payment_opration_type = fields.Selection([('cancel','Cancel'),('draft','Cancel and Set to Draft'),('delete','Cancel and Delete')],string='Payment Opration Type', related="company_id.payment_opration_type" ,readonly=False)