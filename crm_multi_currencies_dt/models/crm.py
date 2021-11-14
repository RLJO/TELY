#!/usr/bin/python
# coding: utf8
# from openerp import fields, models, api, _
# from datetime import datetime, timedelta, date
# from dateutil.relativedelta import relativedelta
# from openerp import tools
#
# import logging
# _logger = logging.getLogger(__name__)
#
#
# class crm_lead(models.Model):
#     _inherit = 'crm.lead'
#
#     darb_planned_revenue_currency = fields.Float('Expected Revenue Currency', track_visibility='always', readonly=0)
#     darb_change_currency = fields.Float('Exchange Rate', compute="get_last_change")
#     partner_crm_currency_id = fields.Many2one('res.currency', string="Currency", help='Utility field to express amount currency', related='partner_id.partner_currency_id')
#
#     @api.model
#     def create(self, vals):
#         res = super(crm_lead, self).create(vals)
#         res.planned_revenue = res.darb_planned_revenue_currency * res.darb_change_currency
#         print "res.planned_revenue"
#         print res.planned_revenue
#         return res
#
#
#     @api.multi
#     @api.onchange('partner_id','darb_planned_revenue_currency','darb_change_currency', 'planned_revenue')
#     @api.depends('partner_id','darb_planned_revenue_currency')
#     def get_last_change(self):
#         for s in self:
#             company_cur = s.env['res.company'].search([('id','!=',False)]).currency_id.id
#             s.company_currency = company_cur
#
#             print " s.env['res.currency.rate'].search([('currency_id.id','=',s.partner_id.partner_currency_id.id)],order=)"
#             print  s.env['res.currency.rate'].search([('currency_id.id','=',s.partner_id.partner_currency_id.id)],order="name")
#             if s.partner_id.partner_currency_id.id:
#                 if s.partner_id.partner_currency_id.id != company_cur:
#                     if s.planned_revenue != 0 and s.darb_planned_revenue_currency == 0 :
#                         print "revenu before"
#                         print s.darb_planned_revenue_currency
#                         s.darb_change_currency = s.env['res.currency'].search([('id','=',s.partner_id.partner_currency_id.id)]).rate
#                         print "taux"
#                         print s.darb_change_currency
#                         s.darb_planned_revenue_currency = s.planned_revenue / s.darb_change_currency
#                         print "revenu"
#                         print s.planned_revenue
#                         print "revenu before"
#                         print s.darb_planned_revenue_currency
#
#                     # if s.planned_revenue == s.darb_planned_revenue_currency and s.darb_change_currency != 1:
#                     #     print "revenu before"
#                     #     print s.darb_planned_revenue_currency
#                     #     s.darb_change_currency = s.env['res.currency'].search([('id','=',s.partner_id.partner_currency_id.id)]).rate
#                     #     print "taux"
#                     #     print s.darb_change_currency
#                     #     s.darb_planned_revenue_currency = s.planned_revenue / s.darb_change_currency
#                     #     print "revenu"
#                     #     print s.planned_revenue
#                     #     print "revenu before"
#                     #     print s.darb_planned_revenue_currency
#
#                     else:
#                         s.darb_change_currency = s.env['res.currency'].search(
#                             [('id', '=', s.partner_id.partner_currency_id.id)]).rate
#                         s.planned_revenue = s.darb_planned_revenue_currency * s.darb_change_currency
#
#                         print "else"
#                         print "revenu"
#                         print s.planned_revenue
#                         print "taux"
#                         print s.darb_change_currency
#                         print "revenu before"
#                         print s.darb_planned_revenue_currency
#
#                 else:
#                     print "else 2"
#                     s.darb_change_currency = 1
#                     if s.planned_revenue != 0 and  s.darb_planned_revenue_currency == 0:
#                         s.darb_planned_revenue_currency = s.planned_revenue
#                     else:
#                         s.planned_revenue = s.darb_planned_revenue_currency
#
#             else:
#                 print "else 3"
#                 s.darb_change_currency = 1
#                 # if s.planned_revenue == 0 and s.darb_planned_revenue_currency != 0:
#                 #     s.planned_revenue = s.darb_planned_revenue_currency
#                 # if s.planned_revenue != 0 and s.darb_planned_revenue_currency == 0:
#                 s.darb_planned_revenue_currency = s.planned_revenue
#                 # if s.planned_revenue != 0 and s.darb_planned_revenue_currency != 0:
#                 #     s.planned_revenue = s.darb_planned_revenue_currency
#

#!/usr/bin/python
# coding: utf8
from openerp import fields, models, api, _
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from openerp import tools

import logging
_logger = logging.getLogger(__name__)

class crm_lead(models.Model):
    _inherit = 'crm.lead'

    darb_planned_revenue_currency = fields.Float('Expected Revenue', track_visibility='always', readonly=0)
    darb_change_currency = fields.Float('With Exchange Rate', compute="get_last_change", default = 1, store=True)
    partner_crm_currency_id = fields.Many2one('res.currency', string="Currency", help='Utility field to express amount currency', related='partner_id.partner_currency_id')

    @api.multi
    @api.onchange('partner_id','darb_planned_revenue_currency')
    @api.depends('partner_id','darb_planned_revenue_currency','partner_id.partner_currency_id','partner_id.partner_currency_id.rate_ids.rate')
    def get_last_change(self):
        for s in self:
            _logger.info("Current records" + str(self._ids))
            user_id = self.env['res.users'].search([('id','=',self.env.uid)])
            company_cur = s.env['res.company'].search([('id','=',user_id.company_id.id)]).currency_id.id
            s.company_currency = company_cur
            if s.partner_id.partner_currency_id.id:
                if s.partner_id.partner_currency_id.id != s.company_currency.id:
                    s.darb_change_currency = s.env['res.currency'].search([('id','=',s.partner_id.partner_currency_id.id)]).rate
                    if s.planned_revenue != 0 and s.darb_planned_revenue_currency == 0:
                        if type(s.id) == int:
                            self.env.cr.execute('update crm_lead set darb_planned_revenue_currency=%s where id=%s', (s.planned_revenue / s.darb_change_currency, s.id))
                        else:
                            s.darb_planned_revenue_currency = s.planned_revenue / s.darb_change_currency
                    else:
                        if type(s.id) == int:
                            self.env.cr.execute('update crm_lead set planned_revenue=%s where id=%s', (s.darb_planned_revenue_currency * s.darb_change_currency, s.id))
                        else:
                            s.planned_revenue = s.darb_planned_revenue_currency * s.darb_change_currency
                else:
                    s.darb_change_currency = 1
                    if s.planned_revenue != 0 and s.darb_planned_revenue_currency == 0:
                        if type(s.id) == int:
                            self.env.cr.execute('update crm_lead set darb_planned_revenue_currency=%s where id=%s', (s.planned_revenue, s.id))
                        else:
                            s.darb_planned_revenue_currency = s.planned_revenue
                    else:
                        if type(s.id) == int:
                            self.env.cr.execute('update crm_lead set planned_revenue=%s where id=%s', (s.darb_planned_revenue_currency, s.id))
                        else:
                            s.planned_revenue = s.darb_planned_revenue_currency
            else:
                s.darb_change_currency = 1
                if s.planned_revenue != 0 and s.darb_planned_revenue_currency == 0:
                    if type(s.id) == int:
                        self.env.cr.execute('update crm_lead set darb_planned_revenue_currency=%s where id=%s', (s.planned_revenue, s.id))
                    else:
                        s.darb_planned_revenue_currency = s.planned_revenue
                else:
                    if type(s.id) == int:
                        self.env.cr.execute('update crm_lead set planned_revenue=%s where id=%s', (s.darb_planned_revenue_currency, s.id))
                    else:
                        s.planned_revenue = s.darb_planned_revenue_currency

    """@api.model_cr
    def init(self):
        self.env.cr.execute(
            "UPDATE crm_lead SET darb_planned_revenue_currency = planned_revenue/darb_change_currency  ", )

        return True

    @api.model
    def create(self, vals):
        res = super(crm_lead, self).create(vals)
        res.planned_revenue = res.darb_planned_revenue_currency * res.darb_change_currency
        print "res.planned_revenue"
        print res.planned_revenue
        return res

    @api.multi
    @api.onchange('partner_id','darb_planned_revenue_currency','darb_change_currency')
    @api.depends('partner_id','darb_planned_revenue_currency','darb_change_currency')
    def get_last_change(self):
        for s in self:
            company_cur = s.env['res.company'].search([('id','!=',False)]).currency_id.id
            s.company_currency = company_cur

            print " s.env['res.currency.rate'].search([('currency_id.id','=',s.partner_id.partner_currency_id.id)],order=)"
            print  s.env['res.currency.rate'].search([('currency_id.id','=',s.partner_id.partner_currency_id.id)],order="name")
            if s.partner_id.partner_currency_id.id:
                if s.partner_id.partner_currency_id.id != company_cur:
                    if s.planned_revenue != 0 and  s.darb_planned_revenue_currency == 0:
                        print "revenu before"
                        print s.darb_planned_revenue_currency
                        s.darb_change_currency = s.env['res.currency'].search([('id','=',s.partner_id.partner_currency_id.id)]).rate
                        print "taux"
                        print s.darb_change_currency
                        s.darb_planned_revenue_currency = s.planned_revenue / s.darb_change_currency
                        print "revenu"
                        print s.planned_revenue
                        print "revenu before"
                        print s.darb_planned_revenue_currency
                    else:
                        s.darb_change_currency = s.env['res.currency'].search(
                            [('id', '=', s.partner_id.partner_currency_id.id)]).rate
                        s.planned_revenue = s.darb_planned_revenue_currency * s.darb_change_currency
                        print "revenu1"
                        print s.planned_revenue
                        s.write({'planned_revenue' : s.darb_planned_revenue_currency * s.darb_change_currency})


                        print "else"
                        print "revenu"
                        print s.planned_revenue
                        print "s.darb_change_currency"
                        print s.darb_change_currency
                        print "revenu before"
                        print s.darb_planned_revenue_currency

                else:
                    print "else 2"
                    s.darb_change_currency = 1
                    if s.planned_revenue != 0 and  s.darb_planned_revenue_currency == 0:
                        s.darb_planned_revenue_currency = s.planned_revenue
                    else:
                        s.planned_revenue = s.darb_planned_revenue_currency

            else:
                print "else 3"
                s.darb_change_currency = 1
                if s.planned_revenue == 0 and s.darb_planned_revenue_currency != 0:
                    s.planned_revenue = s.darb_planned_revenue_currency
                if s.planned_revenue != 0 and s.darb_planned_revenue_currency == 0:
                    s.darb_planned_revenue_currency = s.planned_revenue
                if s.planned_revenue != 0 and s.darb_planned_revenue_currency != 0:
                    s.planned_revenue = s.darb_planned_revenue_currency"""
