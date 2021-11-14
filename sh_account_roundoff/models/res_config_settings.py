# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    sh_enable_round_off = fields.Boolean(
        'Enable Round Off')

    sh_round_off_account_id = fields.Many2one(
        'account.account', string="Round Off Account")


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    sh_enable_round_off = fields.Boolean(
        'Enable Round Off', related='company_id.sh_enable_round_off', readonly=False)

    sh_round_off_account_id = fields.Many2one('account.account',
                                              related='company_id.sh_round_off_account_id', string="Round Off Account", readonly=False)
