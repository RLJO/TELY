# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools import float_compare, float_round, float_is_zero, pycompat

class PurchaseOrder(models.Model):
	_inherit ='purchase.order'
	
	purchase_manual_currency_rate_active = fields.Boolean('Apply Manual Exchange')
	purchase_manual_currency_rate = fields.Float('Rate', digits=(12, 6))

class PurchaseOrderLine(models.Model):
	_inherit ='purchase.order.line'


	@api.multi
	def _prepare_stock_moves(self, picking):
		""" Prepare the stock moves data for one order line. This function returns a list of
		dictionary ready to be used in stock.move's create()
		"""

		rec  = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
		seller = self.product_id._select_seller(
			partner_id=self.partner_id,
			quantity=self.product_qty,
			date=self.order_id.date_order,
			uom_id=self.product_uom)
		
		price_unit = self.env['account.tax']._fix_tax_included_price_company(seller.price, self.product_id.supplier_taxes_id, self.taxes_id, self.company_id) if seller else 0.0
		if price_unit and seller and self.order_id.currency_id and seller.currency_id != self.order_id.currency_id:
			price_unit = seller.currency_id.compute(price_unit, self.order_id.currency_id)

		if seller and self.product_uom and seller.product_uom != self.product_uom:
			price_unit = seller.product_uom._compute_price(price_unit, self.product_uom)
		
		if self.order_id.purchase_manual_currency_rate_active:
			price_unit = self.order_id.currency_id.round((self.price_unit)/self.order_id.purchase_manual_currency_rate)
		
		for line in rec :
			line.update({'price_unit' : price_unit})

		return rec



	
	@api.onchange('product_qty', 'product_uom')
	def _onchange_quantity(self):
		if not self.product_id:
			return
		params = {'order_id': self.order_id}
		seller = self.product_id._select_seller(
			partner_id=self.partner_id,
			quantity=self.product_qty,
			date=self.order_id.date_order and self.order_id.date_order.date(),
			uom_id=self.product_uom,
			params=params)

		if seller or not self.date_planned:
			self.date_planned = self._get_date_planned(seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

		if not seller:
			if self.product_id.seller_ids.filtered(lambda s: s.name.id == self.partner_id.id):
				self.price_unit = 0.0
			return

		price_unit = self.env['account.tax']._fix_tax_included_price_company(seller.price, self.product_id.supplier_taxes_id, self.taxes_id, self.company_id) if seller else 0.0
		pu = price_unit
		if price_unit and seller and self.order_id.currency_id and seller.currency_id != self.order_id.currency_id:
			price_unit = seller.currency_id._convert(
				price_unit, self.order_id.currency_id, self.order_id.company_id, self.date_order or fields.Date.today())

		if seller and self.product_uom and seller.product_uom != self.product_uom:
			price_unit = seller.product_uom._compute_price(price_unit, self.product_uom)

		if self.order_id.purchase_manual_currency_rate_active:
			price_unit = pu * self.order_id.purchase_manual_currency_rate

		self.price_unit = price_unit


class StockMove(models.Model):
	_inherit = "stock.move"



	def _run_valuation(self, quantity=None):
		self.ensure_one()
		value_to_return = 0
		if self._is_in():
			valued_move_lines = self.move_line_ids.filtered(lambda ml: not ml.location_id._should_be_valued() and ml.location_dest_id._should_be_valued() and not ml.owner_id)
			valued_quantity = 0
			for valued_move_line in valued_move_lines:
				valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, self.product_id.uom_id)

			# Note: we always compute the fifo `remaining_value` and `remaining_qty` fields no
			# matter which cost method is set, to ease the switching of cost method.
			vals = {}
			price_unit = self._get_price_unit()
			if self.purchase_line_id :

				if self.purchase_line_id.order_id.purchase_manual_currency_rate_active:
					price_unit = self.purchase_line_id.order_id.currency_id.round((self.purchase_line_id.price_unit)/self.purchase_line_id.order_id.purchase_manual_currency_rate)

			value = price_unit * (quantity or valued_quantity)
			value_to_return = value if quantity is None or not self.value else self.value
			
			vals = {
				'price_unit': price_unit,
				'value': value_to_return,
				'remaining_value': value if quantity is None else self.remaining_value + value,
			}
			vals['remaining_qty'] = valued_quantity if quantity is None else self.remaining_qty + quantity

			if self.product_id.cost_method == 'standard':
				value = self.product_id.standard_price * (quantity or valued_quantity)
				value_to_return = value if quantity is None or not self.value else self.value
				vals.update({
					'price_unit': self.product_id.standard_price,
					'value': value_to_return,
				})
			self.write(vals)
		elif self._is_out():
			valued_move_lines = self.move_line_ids.filtered(lambda ml: ml.location_id._should_be_valued() and not ml.location_dest_id._should_be_valued() and not ml.owner_id)
			valued_quantity = 0
			for valued_move_line in valued_move_lines:
				valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, self.product_id.uom_id)
			self.env['stock.move']._run_fifo(self, quantity=quantity)
			if self.product_id.cost_method in ['standard', 'average']:
				curr_rounding = self.company_id.currency_id.rounding
				value = -float_round(self.product_id.standard_price * (valued_quantity if quantity is None else quantity), precision_rounding=curr_rounding)
				value_to_return = value if quantity is None else self.value + value
				self.write({
					'value': value_to_return,
					'price_unit': value / valued_quantity,
				})
		elif self._is_dropshipped() or self._is_dropshipped_returned():
			curr_rounding = self.company_id.currency_id.rounding
			if self.product_id.cost_method in ['fifo']:
				price_unit = self._get_price_unit()
				# see test_dropship_fifo_perpetual_anglosaxon_ordered
				self.product_id.standard_price = price_unit
			else:
				price_unit = self.product_id.standard_price
			value = float_round(self.product_qty * price_unit, precision_rounding=curr_rounding)
			value_to_return = value if self._is_dropshipped() else -value
			# In move have a positive value, out move have a negative value, let's arbitrary say
			# dropship are positive.
			self.write({
				'value': value_to_return,
				'price_unit': price_unit if self._is_dropshipped() else -price_unit,
			})
		return value_to_return


class AccountInvoice(models.Model):
	_inherit = 'account.invoice'

	@api.onchange('purchase_id')
	def purchase_order_change(self):
		if not self.purchase_id:
			return {}
		if not self.partner_id:
			self.partner_id = self.purchase_id.partner_id.id

		vendor_ref = self.purchase_id.partner_ref
		if vendor_ref and (not self.reference or (
				vendor_ref + ", " not in self.reference and not self.reference.endswith(vendor_ref))):
			self.reference = ", ".join([self.reference, vendor_ref]) if self.reference else vendor_ref

		if self.purchase_id.purchase_manual_currency_rate_active:
			self.manual_currency_rate_active = self.purchase_id.purchase_manual_currency_rate_active
			self.manual_currency_rate = self.purchase_id.purchase_manual_currency_rate
			self.currency_id = self.purchase_id.currency_id.id


		new_lines = self.env['account.invoice.line']
		for line in self.purchase_id.order_line - self.invoice_line_ids.mapped('purchase_line_id'):
			data = self._prepare_invoice_line_from_po_line(line)
			new_line = new_lines.new(data)
			new_line._set_additional_fields(self)
			new_lines += new_line


		self.invoice_line_ids += new_lines
		self.payment_term_id = self.purchase_id.payment_term_id
		self.env.context = dict(self.env.context, from_purchase_order_change=True)
		self.purchase_id = False
		return {}


	@api.onchange('journal_id')
	def _onchange_journal_id(self):
		if self.journal_id:
			currency = self.journal_id.company_id.currency_id.id
			purchase = self.purchase_id
			if not purchase:
				purchase = self.env['purchase.order'].search([('name','ilike',self.origin)])

			if purchase:
				if purchase.purchase_manual_currency_rate_active:
					currency = purchase.currency_id.id or currency

			self.currency_id = self.journal_id.currency_id.id or currency


	
