# -*- coding: utf-8 -*-
# Copyright 2018 Sodexis
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, api, fields, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_method_id = fields.Many2one(
        'account.journal', domain=[('at_least_one_inbound', '=', True),
            ('type', 'in', ['bank', 'cash'])
        ],
        string='Payment Method', copy=False,
    )
    
    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super(SaleOrder, self).onchange_partner_id()
        for order in self:
            order.payment_method_id = order.partner_id.sale_payment_method_id
        return res
