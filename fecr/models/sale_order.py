# -*- coding: utf-8 -*-
import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    conditions = fields.Text(string=u'Condiciones técnicas')
    terms_contract = fields.Text(string=u'Términos de contrato')
    important = fields.Text(string='Importante')
    detalle = fields.Char('Detalle (Especificar detalle)')
    plain_paid_lines = fields.One2many('sale.order.plain_paids', 'order_id')

    payment_method_id = fields.Many2one('payment.methods',string=u'Método de pago',related='partner_id.payment_methods_id',store=True,copy=False, states={'draft': [('readonly', False)]})

    apply_terms_conditions = fields.Boolean()

    #Conversión a USD
    @api.model
    def default_usd(self):
        usd_id = self.env.ref('base.USD').id
        usd_currency = self.env['res.currency'].sudo().browse(usd_id)
        return usd_currency

    currency_usd_id = fields.Many2one('res.currency', default=default_usd, string='Moneda USD')
    amount_usd = fields.Monetary(currency_field='currency_usd_id', compute='_compute_total_usd', store=True,
                                 readonly=True)
    monto_usd = fields.Monetary(currency_field='currency_usd_id', string=u'Monto en Dólares', store=True)


    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(SaleOrder, self).onchange_partner_id()
        if len(self.partner_id.payment_methods_id) > 0:
            self.payment_method_id = self.partner_id.payment_methods_id

    @api.multi
    def _prepare_invoice(self):
        """
        SOBREESCRITURA DEL MÉTODO ORIGINAL: JMack
        """
        self.ensure_one()
        company_id = self.company_id.id
        journal_id = (self.env['account.invoice'].with_context(company_id=company_id or self.env.user.company_id.id)
            .default_get(['journal_id'])['journal_id'])
        if not journal_id:
            raise UserError(_('Please define an accounting sales journal for this company.'))
        return {
            'name': (self.client_order_ref or '')[:2000],
            'origin': self.name,
            'type': 'out_invoice',
            'account_id': self.partner_invoice_id.property_account_receivable_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'journal_id': journal_id,
            'currency_id': self.pricelist_id.currency_id.id,
            'comment': self.note,
            'partner_id': self.partner_invoice_id.id,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': company_id,
            'user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id,
            'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            'payment_methods_id' : self.payment_method_id.id or self.partner_id.payment_methods_id.id
        }

    @api.depends('amount_total', 'pricelist_id', 'date_order')
    def _compute_total_usd(self):
        for so in self:
            rates = so.currency_usd_id.rate_ids
            if so.pricelist_id:
                if so.pricelist_id.currency_id.id != so.currency_usd_id.id:
                    date = self._get_date_convert(rates, so.date_order.date())
                    so.amount_usd = so.pricelist_id.currency_id._convert(so.amount_total, so.currency_usd_id,
                                                                         so.company_id,
                                                                         date)
                    so.monto_usd = so.amount_usd
                else:
                    so.amount_usd = so.amount_total
                    so.monto_usd = so.amount_usd

    @api.model_cr
    def init(self):
        for so in self.env['sale.order'].sudo().search([]):
            rates = so.currency_usd_id.rate_ids
            if so.pricelist_id:
                if so.pricelist_id.currency_id.id != so.currency_usd_id.id:
                    date = self._get_date_convert(rates, so.date_order.date())
                    so.amount_usd = so.pricelist_id.currency_id._convert(so.amount_total, so.currency_usd_id,
                                                                         so.company_id, date)
                    so.monto_usd = so.amount_usd
                else:
                    so.amount_usd = so.amount_total
                    so.monto_usd = so.amount_usd

    def _get_date_convert(self, rates, so_date):
        date = rates.filtered(lambda f: f.name == so_date)
        if not date:
            date = rates.filtered(lambda f: f.name <= so_date)

        if date:
            return date[0].name
        else:
            return datetime.date.today()


class PlainPaidLines(models.Model):
    _name = "sale.order.plain_paids"
    _description = "Plan de Pagos"

    order_id = fields.Many2one('sale.order')
    hito = fields.Char('Hito')
    currency_id = fields.Many2one(related='order_id.currency_id', depends=['order_id.currency_id'], store=True, string='Moneda', readonly=True)
    monto = fields.Monetary('Monto')
    fecha = fields.Date('Fecha')
