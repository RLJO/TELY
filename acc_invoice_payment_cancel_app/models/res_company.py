# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    invoice_opration_type = fields.Selection([('cancel','Cancel'),('draft','Cancel and Set to Draft'),('delete','Cancel and Delete')],string='Invoice Type')
    payment_opration_type = fields.Selection([('cancel','Cancel'),('draft','Cancel and Set to Draft'),('delete','Cancel and Delete')],string='Payment Type')