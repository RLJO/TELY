# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api,_
from odoo.exceptions import UserError

class account_invoice_line(models.Model):
    _inherit ='account.invoice.line'
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(account_invoice_line, self)._onchange_product_id()
        if self.invoice_id.manual_currency_rate_active:
            manual_currency_rate = self.product_id.lst_price * self.invoice_id.manual_currency_rate
            self.price_unit = manual_currency_rate
            self.name = self.product_id.name
        if self.invoice_id.manual_currency_rate_active is False:
            manual_currency_rate = self.product_id.lst_price
            self.price_unit = manual_currency_rate
            self.name = self.product_id.name
        return res
        
    '''@api.onchange('product_id')
    def _onchange_product_id(self):
        if not self.invoice_id:
            return
        if self.invoice_id.manual_currency_rate_active:
            manual_currency_rate = self.product_id.lst_price * self.invoice_id.manual_currency_rate
            self.price_unit = manual_currency_rate
            self.name = self.product_id.name
        if self.invoice_id.manual_currency_rate_active is False:
            manual_currency_rate = self.product_id.lst_price
            self.price_unit = manual_currency_rate
            self.name = self.product_id.name'''
        
class account_invoice(models.Model):
    _inherit ='account.invoice'
    
    manual_currency_rate_active = fields.Boolean('Apply Manual Exchange')
    manual_currency_rate = fields.Float('Rate', digits=(12, 6))

    # @api.multi
    # def action_move_create(self):
    #     """ Creates invoice related analytics and financial move lines """
    #     account_move = self.env['account.move']
    #     price = False
    #     for inv in self:
    #         if not inv.journal_id.sequence_id:
    #             raise UserError(_('Please define sequence on the journal related to this invoice.'))
    #         if not inv.invoice_line_ids:
    #             raise UserError(_('Please create some invoice lines.'))
    #         if inv.move_id:
    #             continue
    #
    #         ctx = dict(self._context, lang=inv.partner_id.lang)
    #         if not inv.date_invoice:
    #             inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
    #         date_invoice = inv.date_invoice
    #         company_currency = inv.company_id.currency_id
    #
    #         # create move lines (one per invoice line + eventual taxes and analytic lines)
    #         iml = inv.invoice_line_move_line_get()
    #         iml += inv.tax_line_move_line_get()
    #
    #         diff_currency = inv.currency_id != company_currency
    #         # create one move line for the total and possibly adjust the other lines amount
    #         total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)
    #
    #         name = inv.name or '/'
    #         if inv.payment_term_id:
    #             totlines = inv.with_context(ctx).payment_term_id.with_context(currency_id=company_currency.id).compute(total, date_invoice)[0]
    #             res_amount_currency = total_currency
    #             ctx['date'] = date_invoice
    #             for i, t in enumerate(totlines):
    #                 if inv.currency_id != company_currency:
    #                     amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
    #                 else:
    #                     amount_currency = False
    #
    #                 # last line: add the diff
    #                 res_amount_currency -= amount_currency or 0
    #                 if i + 1 == len(totlines):
    #                     amount_currency += res_amount_currency
    #                 if inv.manual_currency_rate_active:
    #
    #                     iml.append({
    #                         'type': 'dest',
    #                         'name': name,
    #                         'price': price,
    #                         'account_id': inv.account_id.id,
    #                         'date_maturity': t[0],
    #                         'amount_currency': diff_currency and amount_currency,
    #                         'currency_id': diff_currency and inv.currency_id.id,
    #                         'invoice_id': inv.id
    #                     })
    #                 else:
    #                     iml.append({
    #                         'type': 'dest',
    #                         'name': name,
    #                         'price': t[1],
    #                         'account_id': inv.account_id.id,
    #                         'date_maturity': t[0],
    #                         'amount_currency': diff_currency and amount_currency,
    #                         'currency_id': diff_currency and inv.currency_id.id,
    #                         'invoice_id': inv.id
    #                     })
    #         else:
    #             iml.append({
    #                 'type': 'dest',
    #                 'name': name,
    #                 'price': price if price else total,
    #                 'account_id': inv.account_id.id,
    #                 'date_maturity': inv.date_due,
    #                 'amount_currency': diff_currency and total_currency,
    #                 'currency_id': diff_currency and inv.currency_id.id,
    #                 'invoice_id': inv.id
    #             })
    #         if inv.manual_currency_rate_active:
    #             for i in iml:
    #                 if inv.manual_currency_rate != 0:
    #                     price = i.get('amount_currency') / inv.manual_currency_rate
    #                     if i.get('price') > 0 or i.get('type') == 'dest':
    #                         i.update({'price':price})
    #                     else:
    #                         i.update({'price':-price})
    #         part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
    #         line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
    #         line = inv.group_lines(iml, line)
    #
    #         journal = inv.journal_id.with_context(ctx)
    #         line = inv.finalize_invoice_move_lines(line)
    #         date = inv.date or date_invoice
    #         move_vals = {
    #             'ref': inv.reference,
    #             'line_ids': line,
    #             'journal_id': journal.id,
    #             'date': date,
    #             'narration': inv.comment,
    #         }
    #         ctx['company_id'] = inv.company_id.id
    #         ctx['invoice'] = inv
    #         ctx_nolang = ctx.copy()
    #         ctx_nolang.pop('lang', None)
    #         move = account_move.with_context(ctx_nolang).create(move_vals)
    #         # Pass invoice in context in method post: used if you want to get the same
    #         # account move reference when creating the same invoice after a cancelled one:
    #         move.post()
    #         # make the invoice point to that move
    #         vals = {
    #             'move_id': move.id,
    #             'date': date,
    #             'move_name': move.name,
    #         }
    #         inv.with_context(ctx).write(vals)
    #     return True

class stock_move(models.Model):
    _inherit = 'stock.move'




    def _get_price_unit(self):
        """ Returns the unit price to store on the quant """
        res = super(stock_move, self)._get_price_unit()

        
        if self.purchase_line_id.order_id.purchase_manual_currency_rate_active:
            total = self.purchase_line_id.order_id.currency_id.round(self.purchase_line_id.price_unit/self.purchase_line_id.order_id.purchase_manual_currency_rate)
            

            if total> 0 :
                return total

        return res


    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id):
        """
        Generate the account.move.line values to post to track the stock valuation difference due to the
        processing of the given quant.
        """
        self.ensure_one()

        if self._context.get('force_valuation_amount'):
            valuation_amount = self._context.get('force_valuation_amount')
        else:
            valuation_amount = cost

        # the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
        # the company currency... so we need to use round() before creating the accounting entries.
        debit_value = self.company_id.currency_id.round(valuation_amount)

        # check that all data is correct
        if self.company_id.currency_id.is_zero(debit_value):
            raise UserError(_("The cost of %s is currently equal to 0. Change the cost or the configuration of your product to avoid an incorrect valuation.") % (self.product_id.display_name,))
        credit_value = debit_value


        valuation_partner_id = self._get_partner_id_for_valuation_lines()
        if self.purchase_line_id.order_id.purchase_manual_currency_rate_active:
            debit_value = self.purchase_line_id.order_id.currency_id.round((self.purchase_line_id.price_unit*qty)/self.purchase_line_id.order_id.purchase_manual_currency_rate)
            credit_value = debit_value
            res = [(0, 0, line_vals) for line_vals in self._generate_valuation_lines_data(valuation_partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id).values()]
        else:      
            res = [(0, 0, line_vals) for line_vals in self._generate_valuation_lines_data(valuation_partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id).values()]
        if self.sale_line_id.order_id.sale_manual_currency_rate:
            debit_value = self.sale_line_id.order_id.currency_id.round((self.sale_line_id.price_unit*qty)/self.sale_line_id.order_id.sale_manual_currency_rate)
            credit_value = debit_value
            res = [(0, 0, line_vals) for line_vals in self._generate_valuation_lines_data(valuation_partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id).values()]
        else:      
            res = [(0, 0, line_vals) for line_vals in self._generate_valuation_lines_data(valuation_partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id).values()]

        return res

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id):
        # This method returns a dictonary to provide an easy extension hook to modify the valuation lines (see purchase for an example)
        company_currency = self.company_id.currency_id
        diff_currency = self.purchase_line_id.order_id.currency_id != company_currency
        ctx = dict(self._context, lang=self.purchase_line_id.order_id.partner_id.lang)
        self.ensure_one()

        if self._context.get('forced_ref'):
            ref = self._context['forced_ref']
        else:
            ref = self.picking_id.name
        if self.purchase_line_id:
            debit_line_vals = {
                'name': self.name,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'ref': ref,
                'partner_id': partner_id,
                'debit': debit_value if debit_value > 0 else 0,
                'credit': -debit_value if debit_value < 0 else 0,
                'account_id': debit_account_id,
                'amount_currency': diff_currency and (self.purchase_line_id.price_unit)*qty,
                'currency_id': diff_currency and self.purchase_line_id.order_id.currency_id.id,
            }

            credit_line_vals = {
                'name': self.name,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'ref': ref,
                'partner_id': partner_id,
                'credit': credit_value if credit_value > 0 else 0,
                'debit': -credit_value if credit_value < 0 else 0,
                'account_id': credit_account_id,
                'amount_currency': diff_currency and (-self.purchase_line_id.price_unit)*qty,
                'currency_id': diff_currency and self.purchase_line_id.order_id.currency_id.id,
            }
        elif self.sale_line_id:
            debit_line_vals = {
                'name': self.name,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'ref': ref,
                'partner_id': partner_id,
                'debit': debit_value if debit_value > 0 else 0,
                'credit': -debit_value if debit_value < 0 else 0,
                'account_id': debit_account_id,
                'amount_currency': diff_currency and (-self.sale_line_id.price_unit)*qty,
                'currency_id': diff_currency and self.sale_line_id.order_id.currency_id.id,
            }

            credit_line_vals = {
                'name': self.name,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'ref': ref,
                'partner_id': partner_id,
                'credit': credit_value if credit_value > 0 else 0,
                'debit': -credit_value if credit_value < 0 else 0,
                'account_id': credit_account_id,
                'amount_currency': diff_currency and (self.sale_line_id.price_unit)*qty,
                'currency_id': diff_currency and self.sale_line_id.order_id.currency_id.id,
            }
        else:
            debit_line_vals = {
                    'name': self.name,
                    'product_id': self.product_id.id,
                    'quantity': qty,
                    'product_uom_id': self.product_id.uom_id.id,
                    'ref': ref,
                    'partner_id': partner_id,
                    'debit': debit_value if debit_value > 0 else 0,
                    'credit': -debit_value if debit_value < 0 else 0,
                    'account_id': debit_account_id,
                }

            credit_line_vals = {
                'name': self.name,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'ref': ref,
                'partner_id': partner_id,
                'credit': credit_value if credit_value > 0 else 0,
                'debit': -credit_value if credit_value < 0 else 0,
                'account_id': credit_account_id,
            }

        rslt = {'credit_line_vals': credit_line_vals, 'debit_line_vals': debit_line_vals}
        if credit_value != debit_value:
            # for supplier returns of product in average costing method, in anglo saxon mode
            diff_amount = debit_value - credit_value
            price_diff_account = self.product_id.property_account_creditor_price_difference

            if not price_diff_account:
                price_diff_account = self.product_id.categ_id.property_account_creditor_price_difference_categ
            if not price_diff_account:
                raise UserError(_('Configuration error. Please configure the price difference account on the product or its category to process this operation.'))

            rslt['price_diff_line_vals'] = {
                'name': self.name,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'ref': ref,
                'partner_id': partner_id,
                'credit': diff_amount > 0 and diff_amount or 0,
                'debit': diff_amount < 0 and -diff_amount or 0,
                'account_id': price_diff_account.id,
            }
        return rslt



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
