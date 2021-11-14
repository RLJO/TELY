from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    cancel_done_stock_move = fields.Boolean(string='Cancel Stock Move?')
