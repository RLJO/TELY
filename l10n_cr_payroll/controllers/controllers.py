# -*- coding: utf-8 -*-
from odoo import http

# class L10nCrPayroll(http.Controller):
#     @http.route('/l10n_cr_payroll/l10n_cr_payroll/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/l10n_cr_payroll/l10n_cr_payroll/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('l10n_cr_payroll.listing', {
#             'root': '/l10n_cr_payroll/l10n_cr_payroll',
#             'objects': http.request.env['l10n_cr_payroll.l10n_cr_payroll'].search([]),
#         })

#     @http.route('/l10n_cr_payroll/l10n_cr_payroll/objects/<model("l10n_cr_payroll.l10n_cr_payroll"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('l10n_cr_payroll.object', {
#             'object': obj
#         })