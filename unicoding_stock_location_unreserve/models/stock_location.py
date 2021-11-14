# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class Location(models.Model):
    _inherit = "stock.location"

    def button_unreserve(self):
        self.env['stock.picking'].search([('location_id', '=', self.id), ('state', 'not in', ['done', 'draft', 'cancel'])]).do_unreserve()


    def button_unreserved_all(self):
        stock_quant = self.env['stock.quant'].sudo().search([('location_id', '=', self.id)])
        if stock_quant:
            for sq in stock_quant:
                sq.sudo().write({'reserved_quantity': 0})
