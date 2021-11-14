# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MultipalAccountMoveDraft(models.TransientModel):
	_name = "multipal.account.move.draft.wiz"
	_description = "Multipal Journal Entry Reset To Draft"

	confirm_draft = fields.Boolean(' ')

	@api.multi
	def mass_draft_account_move(self):
		if self.confirm_draft == True:
			for move in self.env['account.move'].browse(self._context.get('active_ids')):
				if move.state in ('cancel'):
					move.state = 'draft'
				elif move.state in ('draft', 'posted'):
					raise ValidationError('You cannot reset Journal Entries, First You have cancel the Journal Entries')
		else:
			raise ValidationError('Please tick the check-box to make sure you want to draft')


	