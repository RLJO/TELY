from odoo import fields, models, api, tools, exceptions, _
import math


class CustomerLoanLine(models.Model):
    _name = 'customer.loan.line'
    _description = 'Loan Installment'
    _inherit = ['mail.thread']
    _rec_name = 'loan_id'

    due_date = fields.Date(string='Due Date')
    interest = fields.Float('Interest')
    installment = fields.Float('Installment')
    loan_id = fields.Many2one('customer.loan', string='Loan Request', ondelete='cascade')
    acc_move_ids = fields.One2many('account.move','loan_line_id' )
    rate_month = fields.Float(string='Monthly Rate', digits=(16,7))
    paid_date = fields.Date(string='Paid Date', track_visibility='onchange')
    company_id = fields.Many2one('res.company', related='loan_id.company_id')
    currency_id = fields.Many2one('res.currency', related='loan_id.currency_id')
    customer_id = fields.Many2one('res.partner',related='loan_id.customer_id', string='Customer', store=True)
    vendor_id = fields.Many2one('res.partner',related='loan_id.vendor_id', string='Vendor', store=True)
    sr_number = fields.Integer(string='Sequence')
    remaining = fields.Float(string='Remaining Principal')
    paid = fields.Float(string='Total Paid Amount')
    hide_payment_btn = fields.Boolean(string='Hide Payment Amount', compute='compute_invisible_payment_amount')
    rate = fields.Float(string='Total Rate', compute='_calculate_main_rate')
    amount = fields.Float('Principal', compute='_compute_installment')
    status = fields.Selection([('draft', 'Draft'),('cancel', 'Cancelled'), ('paid', 'Paid')], string='Status',default='draft', track_visibility='onchange')

    @api.multi
    def _calculate_main_rate(self):
        for rec in self:
            rec.rate = rec.rate_month*1200

    @api.multi
    def _compute_installment(self):
        for rec in self:
            if rec.installment:
                rec.amount = abs(rec.installment - rec.interest)
   
    @api.multi
    def check_move_amount(self):      
        self.ensure_one()
        interest_moves = self.acc_move_ids.mapped('line_ids').filtered(lambda r: r.account_id == self.loan_id.credit_account_id)
        principal_moves = self.acc_move_ids.mapped('line_ids').filtered(lambda r: r.account_id == self.loan_id.debit_account_id)
        self.interest = (sum(interest_moves.mapped('credit')) - sum(interest_moves.mapped('debit')))
        self.installment = (sum(principal_moves.mapped('debit')))

    def move_vals(self,journal):
        return {'loan_line_id': self.id,'loan_id': self.loan_id.id,'date': self.due_date,'ref': self.loan_id.name,
            'journal_id': journal.id, 'line_ids': [(0, 0, vals) for vals in self.move_line_vals(journal)]}

    def move_line_vals(self,journal):
        vals = []
        partner = self.loan_id.customer_id.with_context(force_company=self.loan_id.company_id.id)
        vals.append({'account_id': journal.default_debit_account_id.id,'partner_id': partner.id,'debit': self.installment,'credit': 0})
        vals.append({'account_id': self.loan_id.interest_account_id.id,'debit': 0,'credit': self.interest})
        vals.append({'account_id': self.loan_id.debit_account_id.id,'debit': 0,'credit': self.installment - self.interest})
       
        return vals

    @api.multi
    def view_process_values(self,journal):
        res = []
        move_obj = self.env['account.move']
        for record in self:
            if not record.acc_move_ids:
                if record.loan_id.line_ids.filtered(lambda r: r.due_date < record.due_date and not r.acc_move_ids):
                    raise exceptions.UserError(_("Please Pay Remaining Installments First."))
                move = move_obj.create(record.move_vals(journal))
                move.post()
                res.append(move.id)

        action = self.env.ref('account.action_move_line_form').read()[0]
        action['context'] = {'default_loan_line_id': self.id,'default_loan_id': self.loan_id.id }
        action['domain'] = [('loan_line_id', '=', self.id)]
        if len(self.acc_move_ids) == 1:
            res = self.env.ref('account.move.form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = self.acc_move_ids.id

        return action

    @api.depends('status','loan_id.status','installment')
    @api.multi
    def compute_invisible_payment_amount(self):
        for rec in self:
            flag = False
            if rec.status == 'draft' and tools.float_round(rec.installment, 2) > 0.0 and rec.loan_id.status == 'approved':
                flag = True
            else:
                flag = False
            rec.hide_payment_btn = flag