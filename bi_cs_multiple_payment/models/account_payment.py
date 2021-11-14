# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError





class account_payment(models.Model):
	_inherit = "account.payment"

	def _create_payment_entry(self, amount):
		""" Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
		Return the journal entry."""
		if 'payment' in self._context:
			
			aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
			invoice_currency = False
			if self.invoice_ids and all([x.currency_id == \
				self.invoice_ids[0].currency_id for x in self.invoice_ids]):
				#if all the invoices selected share the same currency, record the paiement in that currency too
				invoice_currency = self.invoice_ids[0].currency_id

			move = self.env['account.move'].create(self._get_move_vals())
			
			p_id = str(self.partner_id.id)
			
			for inv in self._context.get('payment')[p_id]['inv_val']: 
				#Write line corresponding to invoice payment
				amount = 0.0

				if 'is_customer' in self._context and self._context.get('is_customer'):
					amount = self._context.get('payment')[p_id]['inv_val'][inv]['amount_to_pay'] * (self.payment_type in ('outbound', 'transfer') and 1 or -1)					
				else:
					amount = self._context.get('payment')[p_id]['inv_val'][inv] * (self.payment_type in ('outbound', 'transfer') and 1 or -1)

				debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)
				
				current_invoice = self.env['account.invoice'].browse(int(inv))
				
				counterpart_aml_dict = self._get_shared_move_line_vals\
				(debit, credit, amount_currency, move.id, False)
				counterpart_aml_dict.update(self._get_counterpart_move_line_vals\
				(current_invoice))
				counterpart_aml_dict.update({'currency_id': currency_id})
				counterpart_aml = aml_obj.create(counterpart_aml_dict)

				if 'is_customer' in self._context and self._context.get('is_customer'):
					#Reconcile with the invoices.
					payment_difference = self._context.get('payment')[p_id]['inv_val'][inv]['payment_diff']
					
					if self.payment_difference_handling == 'reconcile' and payment_difference:
						writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
						
						debit_wo, credit_wo, amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(payment_difference, self.currency_id, self.company_id.currency_id)
						# the writeoff debit and credit must be computed from the invoice residual in company currency
						# minus the payment amount in company currency, and not from the payment difference in the payment currency
						# to avoid loss of precision during the currency rate computations. See revision 20935462a0cabeb45480ce70114ff2f4e91eaf79 for a detailed example.
						total_residual_company_signed = sum\
						(invoice.residual_company_signed for invoice in self.invoice_ids)
						total_payment_company_signed = self.currency_id.with_context\
						(date=self.payment_date).compute(self.amount, self.company_id.currency_id)
						if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
							amount_wo = total_payment_company_signed - total_residual_company_signed		
						else:
							amount_wo = total_residual_company_signed - total_payment_company_signed
						# Align the sign of the secondary currency writeoff amount with the sign of the writeoff
						# amount in the company currency
						if amount_wo > 0:
							debit_wo = amount_wo
							credit_wo = 0.0
							amount_currency_wo = abs(amount_currency_wo)
						else:
							debit_wo = 0.0
							credit_wo = -amount_wo
							amount_currency_wo = -abs(amount_currency_wo)
						writeoff_line['name'] = _('Counterpart')
						
						writeoff_line['account_id'] = self.writeoff_account_id.id
						
						writeoff_line['debit'] = debit_wo
						
						writeoff_line['credit'] = credit_wo
						
						writeoff_line['amount_currency'] = amount_currency_wo
						
						writeoff_line['currency_id'] = currency_id
						writeoff_line = aml_obj.create(writeoff_line)
						if counterpart_aml['debit']:
							counterpart_aml['debit'] += credit_wo - debit_wo
						if counterpart_aml['credit']:
							counterpart_aml['credit'] += debit_wo - credit_wo
						counterpart_aml['amount_currency'] -= amount_currency_wo
				current_invoice.register_payment(counterpart_aml)
				#Write counterpart lines
				if not self.currency_id != self.company_id.currency_id:
					amount_currency = 0
				liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
				liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
				aml_obj.create(liquidity_aml_dict)
			move.post()
			
			return move
		return super(account_payment, self)._create_payment_entry(amount)