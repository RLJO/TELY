# -*- coding: utf-8 -*-
# Copyright 2018 Sodexis
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sale_payment_method_id = fields.Many2one(
        'account.journal',
        domain=[
            ('at_least_one_inbound', '=', True),
            ('type', 'in', ['bank', 'cash'])
        ],
        string='Sale Payment Method', copy=False,
    )
