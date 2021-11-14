#!/usr/bin/python
# coding: utf8

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class res_partner(models.Model):
    _inherit = 'res.partner'

    partner_currency_id = fields.Many2one('res.currency', string="Currency", help='Utility field to express amount currency')

    @api.model
    def create(self, values):
        # Override the original create function for the res.partner model
        sale_module = self.env['ir.module.module'].search([
            ('name', '=', 'sale')
        ])
        if sale_module and sale_module.state == 'installed':
            if values['property_product_pricelist']:
                pricelist_id = self.env['product.pricelist'].browse(values['property_product_pricelist'])
                _logger.info("Current products       " + str(pricelist_id.currency_id))
                values['partner_currency_id'] = pricelist_id.currency_id.id
        res = super(res_partner, self).create(values)
        return res

    @api.multi
    def write(self, vals):
        sale_module = self.env['ir.module.module'].search([
            ('name', '=', 'sale')
        ])
        if sale_module and sale_module.state == 'installed':
            if 'property_product_pricelist' in vals:
                pricelist_id = self.env['product.pricelist'].browse(vals['property_product_pricelist'])
                _logger.info("Current products       " + str(pricelist_id.currency_id))
                vals['partner_currency_id'] = pricelist_id.currency_id.id
        return super(res_partner, self).write(vals)
