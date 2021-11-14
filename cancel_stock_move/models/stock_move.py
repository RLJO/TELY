from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def action_cancel(self):

        return self._action_cancel()

    def _action_cancel(self):
        quant_obj = self.env['stock.quant']
        account_move_obj = self.env['account.move']
        for move in self:
            if move.company_id.cancel_done_stock_move:
                if move.state == 'cancel':
                    continue
                if move.state == "done" and move.product_id.type == "product":
                    for move_line in move.move_line_ids:
                        quantity = move_line.product_uom_id._compute_quantity(move_line.qty_done, move_line.product_id.uom_id)
                        quant_obj._update_available_quantity(move_line.product_id, move_line.location_id, quantity,move_line.lot_id)
                        quant_obj._update_available_quantity(move_line.product_id, move_line.location_dest_id, quantity * -1,move_line.lot_id)
                if move.procure_method == 'make_to_order' and not move.move_orig_ids:
                    move.state = 'waiting'
                elif move.move_orig_ids and not all(orig.state in ('done', 'cancel') for orig in move.move_orig_ids):
                    move.state = 'waiting'
                else:
                    move.state = 'confirmed'
                siblings_states = (move.move_dest_ids.mapped('move_orig_ids') - move).mapped('state')
                if move.propagate:
                    # only cancel the next move if all my siblings are also cancelled
                    if all(state == 'cancel' for state in siblings_states):
                        move.move_dest_ids._action_cancel()
                else:
                    if all(state in ('done', 'cancel') for state in siblings_states):
                        move.move_dest_ids.write({'procure_method': 'make_to_stock'})
                    move.move_dest_ids.write({'move_orig_ids': [(3, move.id, 0)]})
                move.write({'state': 'cancel', 'move_orig_ids': [(5, 0, 0)]})
                account_moves = account_move_obj.search([('stock_move_id', '=', move.id)])
                if account_moves:
                    for account_move in account_moves:
                        account_move.quantity_done = 0.0
                        account_move.button_cancel()
                        account_move.unlink()
        return super(StockMove, self)._action_cancel()