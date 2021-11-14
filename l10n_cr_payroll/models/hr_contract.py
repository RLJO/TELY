# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HrContract(models.Model):
    """
    Employee contract based on the visa, work permits
    allows to configure different Salary structure
    """
    _inherit = 'hr.contract'

    x_disponibilidad = fields.Monetary(string='Disponibilidad')
    x_dispsem = fields.Monetary(string='Disponibilidad semanal')
    x_cxc = fields.Monetary(string='Cuentas por cobrar')
    x_emb = fields.Monetary(string='Embargos judiciales')