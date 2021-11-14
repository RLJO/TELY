from datetime import datetime,date
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, exceptions, tools, _
import math,numpy


class CustomerLoan(models.Model):
    _name = 'customer.loan'
    _inherit = ['mail.thread']
    _description = 'Customer Loan'

    @api.depends('line_ids')
    def compute_installment_payment(self):       
        for rec in self:
            total_paid_installment = 0.00
            for inst_line in rec.line_ids:
                if inst_line.status in ['paid','cancel']:
                    total_paid_installment += inst_line.amount
            rec.total_paid = total_paid_installment
            rec.total_remaining = abs(rec.amount - total_paid_installment)

    customer_id = fields.Many2one('res.partner', 'Customer')
    acc_acc_move_ids = fields.One2many('account.move', 'loan_id', copy=False)
    vendor_id = fields.Many2one('res.partner', 'Vendor')
    hide_cancel_reason = fields.Boolean(string='Hide Cancel Reason?', compute='check_interval_in_loan')    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id, string='Company')
    amount = fields.Float('Loan Amount')
    no_of_installment = fields.Integer('No. of Installments', help='How Many Installments?')
    payment_method = fields.Selection([('cash', 'Cash'), ('bank', 'Bank')], string='Payment Method')
    total_paid = fields.Float(compute='compute_installment_payment', string='Total Paid Installment')
    total_remaining = fields.Float(compute='compute_installment_payment', string='Total Remaining Installments')
    debit_account_id = fields.Many2one('account.account',string='Debit Account')
    credit_account_id = fields.Many2one('account.account',string='Credit Account')
    interest_account_id = fields.Many2one('account.account',string='Interest Account')
    loan_issuing_date = fields.Date(string='Installment Start From')
    start_date = fields.Date(string='Installment Start Date', default=date.today(), copy=False)
    accounting_date = fields.Date(string='Accounting Date')
    description = fields.Text('Terms & Condition')
    line_ids = fields.One2many('customer.loan.line', 'loan_id')
    loan_journal_id = fields.Many2one('account.journal', string='Journal')
    loan_approve_date = fields.Date(string='Approved Date')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id.id)
    number_of_interval = fields.Integer(string='Interval', default='1')
    select_period = fields.Selection([('days', 'Days'), ('months', 'Months'), ('years', 'Years')], default='months', string='Period')
    rate = fields.Float(digits=0,help='Currently applied rate',track_visibility='always')
    rate_period = fields.Float(compute='_compute_rate_period', digits=(16, 7))
    name = fields.Char(string="Name", default='New', copy=False)
    hide_interval = fields.Boolean(string='Hide Interval', compute='check_interval_in_loan')    
    process_fee = fields.Float('Processing Fee')
    user_id = fields.Many2one('res.users','Sales Person', default=lambda self: self._uid)
    status = fields.Selection([('draft', 'To Request'), ('waiting', 'Waiting For Approval'), ('approved', 'Confirm'), ('cancel', 'Cancelled'), ('done', 'Done')], default='draft', string='Status',  track_visibility='onchange', copy=False)
    
    @api.depends('company_id')
    def check_interval_in_loan(self):
        for rec in self:
            if rec.company_id.interval_in_loan:
                rec.hide_interval = True
            else:
                rec.hide_interval = False

    @api.constrains('rate','amount', 'no_of_installment')
    def _check_amount(self):
        if self.amount <= 0.00:
            raise exceptions.Warning(_("Please Enter Valid Loan Amount"))

        if self.rate < 0.0:
            raise exceptions.Warning(_("Please Enter Greater Than Zero Rate"))

        if self.no_of_installment <= 0:
            raise exceptions.Warning(_("Please Enter Valid value for Number of Installment"))

    @api.depends('rate')
    def _compute_rate_period(self):
        for rec in self:
            rec.rate_period = (rec.rate/12)/100

    @api.multi
    def view_entry(self):
        action = self.env.ref('account.action_move_line_form').read()[0]
        action['domain'] = [('loan_id', '=', self.id)]
        return action

    @api.multi
    def action_reset_todraft(self):
        self.write({'status':'draft'})
        return True

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('customer.loan') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('customer.loan') or _('New')
        return super(CustomerLoan,self).create(vals)

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.status != 'draft':
                raise exceptions.Warning(_('You cannot Remove Customer Loan.'))
        return super(CustomerLoan, self).unlink()

    @api.multi
    def action_send_approval(self):
        for rec in self:
            rec.status = 'waiting'

    @api.multi
    def approve_loan(self):
        if not self.line_ids:
            self.action_calculation()
        self.write({'status': 'approved', 'accounting_date' : datetime.now(), 'loan_approve_date': datetime.now()})
        self.create_accounting_entry()

    @api.multi
    def action_cancel(self):   
        if any(state=='paid' for state in self.line_ids.mapped('status')):
            raise exceptions.Warning("You can't cancel Loan after installment paid.")

        self.status = 'cancel'
        self.line_ids.write({'status': 'cancel'})

    @api.multi
    def action_calculation(self):
        loan_list = []
        if any(state=='paid' for state in self.line_ids.mapped('status')):
            raise exceptions.Warning("You can't change calculation after installment paid.")
        for rec in self:
            amount = rec.amount
            no_of_installment = rec.no_of_installment
            if amount and no_of_installment:
                amount = amount / no_of_installment
                remaining = rec.amount
                interest = 0
                total_amount = 0.0
                loan_date = self.start_date
                du_date = 0
                # create installment
                for duration in range(1, no_of_installment+1):
                    interval = rec.number_of_interval * duration
                    if rec.select_period == 'days':
                        due_date = loan_date + relativedelta(days=interval)
                    elif rec.select_period == 'years':
                        due_date = loan_date + relativedelta(years=interval)
                    else:
                        due_date = loan_date + relativedelta(months=interval)
                    amt = -(numpy.pmt(rec.rate_period, no_of_installment - duration + 1, remaining))
                    interest = remaining * rec.rate_period
                    remaining = abs(remaining - tools.float_round(amt - interest, 2))
                    vals = {'sr_number': duration,'status': 'draft','due_date': due_date, 'remaining': remaining,
                        'interest': interest,'rate_month': rec.rate_period,
                        'loan_id': rec.id,'installment': amt}
                    total_amount += tools.float_round(amount, 2)
                    loan_list.append((0, 0, vals))
                last_amount = amount - total_amount
                # last installment adding for solve rounding issues
                if last_amount != 0:
                    loan_list[-1][2]['amount'] = loan_list[-1][2].get('installment') + last_amount
                # To remove duplicate lines
            for installment_rec in self.line_ids:
                loan_list.append((2, installment_rec.id))
            self.line_ids = loan_list

    @api.multi
    def clear_installment_line(self):
        if any(state=='paid' for state in self.line_ids.mapped('status')):
            raise exceptions.Warning("You can't clear lines after installment paid.")
        self.write({'line_ids': [(2, self.line_ids.ids)]})

    @api.multi
    def create_accounting_entry(self):
        move_vals = []
        move = self.env['account.move'].create({'journal_id': self.loan_journal_id.id,'company_id':self.env.user.company_id.id,
            'date': self.accounting_date, 'ref': self.name, 'name': '/'  })
        if move:
            vals = { 'name': self.name,'company_id':  self.env.user.company_id.id,
                'currency_id': self.env.user.company_id.currency_id.id,
                'date_maturity': self.loan_issuing_date,'journal_id': self.loan_journal_id.id,
                'date': self.accounting_date, 'customer_id': self.customer_id.id,
                'quantity': 1, 'move_id': move.id }

            debit_vals = {'account_id': self.debit_account_id.id, 'debit': self.amount}
            credit_vals = {'account_id': self.credit_account_id.id, 'credit': self.amount}
            debit_vals.update(vals)
            credit_vals.update(vals)
            move_vals.append((0, 0, debit_vals))
            move_vals.append((0, 0, credit_vals))
            move.line_ids = move_vals or False
            move.loan_id = self.id
            move.post()

    @api.multi
    def action_open_journal_entries(self):
        action = self.env('account.action_move_line_form').read()[0]
        action['domain'] = [('ref', 'in', self.name)]
        return action

    def compute_posted_lines(self):
        amount = self.amount
        for line in self.line_ids.sorted('sr_number'):
            if line.acc_move_ids:
                amount = line.paid_amount
            else:
                line.interest = line.remaining_amount * line.rate_month
                if line.sr_number == line.loan_id.no_of_installment:
                    line.total_amount = line.amount + line.interest
                else:
                    line.total_amount = - numpy.pmt(line.rate_month,line.loan_id.no_of_installment - line.sr_number + 1,line.remaining_amount)
                amount -= line.total_amount - line.inter