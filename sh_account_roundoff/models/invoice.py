# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _check_reconcile_validity(self):
        #Perform all checks on lines
        company_ids = set()
        all_accounts = []
        for line in self:
            company_ids.add(line.company_id.id)
            all_accounts.append(line.account_id)
            if (line.matched_debit_ids or line.matched_credit_ids) and line.reconciled:
                raise UserError(
                    _('You are trying to reconcile some entries that are already reconciled.'))
        if len(company_ids) > 1:
            raise UserError(
                _('To reconcile the entries company should be the same for all entries.'))
#         if len(set(all_accounts)) > 1:
#             raise UserError(_('Entries are not from the same account.'))
        if not (all_accounts[0].reconcile or all_accounts[0].internal_type == 'liquidity'):
            raise UserError(_('Account %s (%s) does not allow reconciliation. First change the configuration of this account to allow it.') % (
                all_accounts[0].name, all_accounts[0].code))


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    sh_round_amount = fields.Monetary(
        "Round Off Amount", store=True, readonly=True, compute='_compute_amount')
    sh_round_off_total = fields.Monetary(
        "Round Off Total", store=True, readonly=True, compute='_compute_amount')

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type', 'date')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(
            line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(line.amount_total)
                              for line in self.tax_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id
            rate_date = self._get_currency_rate_date() or fields.Date.today()
            amount_total_company_signed = currency_id._convert(
                self.amount_total, self.company_id.currency_id, self.company_id, rate_date)
            amount_untaxed_signed = currency_id._convert(
                self.amount_untaxed, self.company_id.currency_id, self.company_id, rate_date)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign
        self.sh_round_off_total = round(self.amount_total)
        self.sh_round_amount = round(self.amount_total) - self.amount_total

    @api.one
    @api.depends(
        'state', 'currency_id', 'invoice_line_ids.price_subtotal',
        'move_id.line_ids.amount_residual',
        'move_id.line_ids.currency_id')
    def _compute_residual(self):
        residual = 0.0
        residual_company_signed = 0.0
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        for line in self._get_aml_for_amount_residual():
            residual_company_signed += line.amount_residual
            if line.currency_id == self.currency_id:
                residual += line.amount_residual_currency if line.currency_id else line.amount_residual
            else:
                if line.currency_id:
                    residual += line.currency_id._convert(
                        line.amount_residual_currency, self.currency_id, line.company_id, line.date or fields.Date.today())
                else:
                    residual += line.company_id.currency_id._convert(
                        line.amount_residual, self.currency_id, line.company_id, line.date or fields.Date.today())

        if self.company_id.sh_enable_round_off:
            self.residual_company_signed = abs(
                round(residual_company_signed)) * sign
            self.residual_signed = abs(round(residual)) * sign
            self.residual = abs(round(residual))
        else:
            self.residual_company_signed = abs(residual_company_signed) * sign
            self.residual_signed = abs(residual) * sign
            self.residual = abs(residual)
        digits_rounding_precision = self.currency_id.rounding
        if float_is_zero(self.residual, precision_rounding=digits_rounding_precision):
            self.reconciled = True
        else:
            self.reconciled = False

    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(
                    _('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids.filtered(lambda line: line.account_id):
                raise UserError(_('Please add at least one invoice line.'))
            if inv.move_id:
                continue

            if not inv.date_invoice:
                inv.write({'date_invoice': fields.Date.context_today(self)})
            if not inv.date_due:
                inv.write({'date_due': inv.date_invoice})
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            iml += inv.tax_line_move_line_get()

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.compute_invoice_totals(
                company_currency, iml)

            name = inv.name or ''
            if inv.payment_term_id:
                totlines = inv.payment_term_id.with_context(
                    currency_id=company_currency.id).compute(total, inv.date_invoice)[0]
                res_amount_currency = total_currency
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency._convert(
                            t[1], inv.currency_id, inv.company_id, inv._get_currency_rate_date() or fields.Date.today())
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id
                })
            part = self.env['res.partner']._find_accounting_partner(
                inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]

            if self.company_id.sh_enable_round_off and self.sh_round_off_total > 0:
                if not self.company_id.sh_round_off_account_id:
                    raise UserError(_("Please set Round of Account !"))
                debit_line = False
                credit_line = False
                for each_line in line:
                    if each_line[2]['account_id'] == self.account_id.id:
                        if each_line[2]['debit'] > 0:
                            each_line[2]['debit'] = self.sh_round_off_total

                            if self.sh_round_off_total < self.amount_total:
                                debit_line = True
                            else:
                                credit_line = True

                        if each_line[2]['credit'] > 0:
                            each_line[2]['credit'] = self.sh_round_off_total

                            if self.sh_round_off_total < self.amount_total:
                                credit_line = True
                            else:
                                debit_line = True
                if debit_line:
                    if self.sh_round_amount < 0:
                        line.append((0, 0, {
                            'account_id': self.company_id.sh_round_off_account_id.id,
                            'debit': self.sh_round_amount * (-1),
                            'credit': 0.0,
                            'name': 'Round Off Amount',

                        }))
                    else:
                        line.append((0, 0, {
                            'account_id': self.company_id.sh_round_off_account_id.id,
                            'debit': self.sh_round_amount,
                            'credit': 0.0,
                            'name': 'Round Off Amount',

                        }))
                if credit_line:
                    if self.sh_round_amount < 0:
                        line.append((0, 0, {
                            'account_id': self.company_id.sh_round_off_account_id.id,
                            'debit': 0.0,
                            'credit': self.sh_round_amount * (-1),
                            'name': 'Round Off Amount',

                        }))
                    else:
                        line.append((0, 0, {
                            'account_id': self.company_id.sh_round_off_account_id.id,
                            'debit': 0.0,
                            'credit': self.sh_round_amount,
                            'name': 'Round Off Amount',

                        }))

            line = inv.group_lines(iml, line)

            line = inv.finalize_invoice_move_lines(line)

            date = inv.date or inv.date_invoice

            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': inv.journal_id.id,
                'date': date,
                'narration': inv.comment,
            }
            move = account_move.create(move_vals)
            # Pass invoice in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post(invoice=inv)
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.write(vals)
        return True
