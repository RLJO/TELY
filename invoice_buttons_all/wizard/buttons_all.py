from odoo import models, fields, api, _
from odoo.tools.float_utils import float_round


class ButtonsAllInvoice(models.TransientModel):
    _name = 'buttons.all.invoice'
    
    def action_invoice_draft_all(self):
        context = dict(self._context or {})
        purchase_obj = self.env['account.invoice']
        active_ids = context.get('active_ids', []) or []
        for line in purchase_obj.browse(active_ids):
            if line.state == 'cancel':
                line.action_draft()
                
        return True
    
    def action_invoice_cancel_all(self):
        context = dict(self._context or {})
        purchase_obj = self.env['account.invoice']
        active_ids = context.get('active_ids', []) or []
        for line in purchase_obj.browse(active_ids):
            if line.state == 'open':
                line.action_invoice_cancel()
                
        return True
    