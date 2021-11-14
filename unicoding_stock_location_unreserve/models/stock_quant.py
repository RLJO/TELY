# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

class StockQuant(models.Model):
    _inherit = "stock.quant"

    def button_unreserve(self):
        for quant in self:
            moves = self.env['stock.move'].search([('location_id', '=', quant.location_id.id), ('product_id', '=', quant.product_id.id),('state', 'not in', ['done', 'draft', 'cancel'])])
            available_quantity = quant.reserved_quantity
            rounding = quant.product_id.uom_id.rounding
            quantity = sum(moves.mapped('product_uom_qty'))
            if float_compare(abs(quantity), available_quantity, precision_rounding=rounding) > 0:
                quant.sudo().write({
                        'reserved_quantity': quantity,
                })


            moves._do_unreserve()


