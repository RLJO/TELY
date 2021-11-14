# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"


    def button_cancels(self):
        if self.company_id.invoice_opration_type == 'cancel':
            self.journal_id.update_posted = True
            self.sudo().action_cancel()
        if self.company_id.invoice_opration_type == 'draft':
            self.journal_id.update_posted = True
            self.sudo().action_cancel()
            self.sudo().action_invoice_draft()
        if self.company_id.invoice_opration_type == 'delete':
            self.journal_id.update_posted = True
            self.move_name = False
            self.sudo().action_cancel()
            self.unlink()

    def account_move_cancel(self):
        account_id =self.env['account.invoice'].browse(self._context.get('active_ids'))
        for move in account_id:
            move.journal_id.update_posted = True
            move.sudo().action_cancel()
            
    def account_move_draft(self):
        account_id =self.env['account.invoice'].browse(self._context.get('active_ids'))
        for move in account_id:
            move.journal_id.update_posted = True
            move.sudo().action_cancel()
            move.sudo().action_invoice_draft()
            
    def account_move_delete(self):
        account_id =self.env['account.invoice'].browse(self._context.get('active_ids'))
        for move in account_id:
            move.journal_id.update_posted = True
            move.move_name = False
            move.sudo().action_cancel()
        account_id.unlink()              