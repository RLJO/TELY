# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_round
from odoo.exceptions import ValidationError

class FullAmountPay(models.TransientModel):
    _name = 'full.amount.pay'
    _description ='Full Amount Pay'

    @api.model
    def _get_default_remaining_amount(self):
        context = dict(self._context)
        loan_obj = self.env['customer.loan']
        if context.get('active_id',False):
            loan_rec = loan_obj.search([('id', '=', context.get('active_id'))])
            if not loan_rec:
                return 0.0
            return loan_rec.total_remaining

    @api.model
    def _default_journal_id(self):
        return self._context.get('default_loan_id') and self._context.get('default_loan_id').journal_id.id or False

    loan_id = fields.Many2one('customer.loan')
    date = fields.Date(required=True, default=fields.Date.today())
    amount = fields.Float(string='Pending Principal', related='loan_id.total_remaining')
    fees = fields.Float(string='Interest')
    total_amount = fields.Float(string='Total Amount',compute='compute_total_amount')
    journal_id = fields.Many2one('account.journal', related='loan_id.loan_journal_id')

    @api.constrains('fees')
    def _check_interest(self):
        if self.fees < 0.00: 
            raise ValidationError(_("Interest Can't Be Greater than Zero(0.00)"))

    @api.depends('amount','fees')
    def compute_total_amount(self):
        for rec in self:
            self.total_amount = self.amount + self.fees

    @api.multi
    def pay_full_amount(self):
        account_move_obj = self.env['account.move']
        res = []
        vals = {
            'loan_id': self.loan_id.id,
            'date': self.date,
            'ref': self.loan_id.name,
            'journal_id': self.journal_id.id,
            'line_ids': [(0, 0, vals) for vals in self.pay_full_amount_line()]}

        move = account_move_obj.create(vals)
        move.post()
        res.append(move.id)
        self.loan_id.status = 'done'
        for line in self.loan_id.line_ids:
            if line.status != 'paid':
                line.status = 'cancel'

    def pay_full_amount_line(self):
        vals = []
        partner = self.loan_id.customer_id.with_context(
            force_company=self.loan_id.company_id.id)
        vals.append({'account_id': self.loan_id.debit_account_id.id,  'partner_id': partner.id, 'debit': self.total_amount,'credit': 0})
        vals.append({'account_id': self.loan_id.credit_account_id.id, 'debit': 0,'credit': self.fees})
        vals.append({'account_id': partner.property_account_payable_id.id, 'debit': 0, 'credit': self.amount})
        return vals
