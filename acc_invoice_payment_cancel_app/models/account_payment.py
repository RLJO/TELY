# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountPayment(models.Model):
    _inherit = "account.payment"


    def button_cancels(self):
        if self.company_id.payment_opration_type == 'cancel':
            self.journal_id.update_posted = True
            self.sudo().cancel()
        if self.company_id.payment_opration_type == 'draft':
            self.journal_id.update_posted = True
            self.sudo().cancel()
            self.sudo().action_draft()
        if self.company_id.payment_opration_type == 'delete':
            self.journal_id.update_posted = True
            self.move_name = False
            self.sudo().cancel()
            self.unlink()


    def account_payment_cancel(self):
        account_id =self.env['account.payment'].browse(self._context.get('active_ids'))
        for payment in account_id:
            payment.journal_id.update_posted = True
            payment.sudo().cancel()
            
    def account_payment_draft(self):
        account_id =self.env['account.payment'].browse(self._context.get('active_ids'))
        for payment in account_id:
            payment.journal_id.update_posted = True
            payment.sudo().cancel()
            payment.action_draft()
            
    def account_payment_delete(self):
        account_id =self.env['account.payment'].browse(self._context.get('active_ids'))
        for payment in account_id:
            payment.move_name = False
            payment.sudo().cancel()
        account_id.unlink()