# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models


class Move(models.Model):
    _inherit = 'stock.move'

    def _sh_unreseve_qty(self):
        for move_line in self.sudo().mapped('move_line_ids'):
            # unreserve qty
            quant = self.env['stock.quant'].sudo().search([('location_id', '=', move_line.location_id.id),
                                                           ('product_id', '=',
                                                            move_line.product_id.id),
                                                           ('lot_id', '=', move_line.lot_id.id)], limit=1)

            if quant:
                quant.write({'quantity': quant.quantity + move_line.qty_done})

            quant = self.env['stock.quant'].sudo().search([('location_id', '=', move_line.location_dest_id.id),
                                                           ('product_id', '=',
                                                            move_line.product_id.id),
                                                           ('lot_id', '=', move_line.lot_id.id)], limit=1)

            if quant:
                quant.write({'quantity': quant.quantity - move_line.qty_done})

    def action_move_cancel(self):
        for rec in self:
            rec.sudo().write({'state': 'cancel'})
            rec.mapped('move_line_ids').sudo().write({'state': 'cancel'})
            rec._sh_unreseve_qty()

    def action_move_cancel_draft(self):
        for rec in self:
            rec.sudo().write({'state': 'draft'})
            rec.mapped('move_line_ids').sudo().write({'state': 'draft'})
            rec._sh_unreseve_qty()

    def action_move_cancel_delete(self):
        for rec in self:
            rec.sudo().write({'state': 'draft'})
            rec.mapped('move_line_ids').sudo().write({'state': 'draft'})
            rec._sh_unreseve_qty()
            rec.mapped('move_line_ids').sudo().unlink()
            rec.sudo().unlink()
