# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
	_inherit = "account.move"
	_description = "Account Move"

	state = fields.Selection(selection_add=[('cancel', 'Cancel')], string='Status')


	@api.multi
	def action_move_draft(self):
		for record in self:
			record.state = 'draft'

