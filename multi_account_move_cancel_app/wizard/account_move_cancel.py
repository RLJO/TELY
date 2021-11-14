# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MultipalAccountMoveCancel(models.TransientModel):
	_name = "multipal.account.move.cancel.wiz"
	_description = "Multipal Journal Entry Cancel"

	confirm_cancel = fields.Boolean(' ')

	@api.multi
	def mass_cancel_account_move(self):
		if self.confirm_cancel == True:
			for move in self.env['account.move'].browse(self._context.get('active_ids')):
				if move.state in ('posted'):
					if move.ids:
						move.mapped('line_ids.analytic_line_ids').unlink()
						move.line_ids.remove_move_reconcile()
						move.check_access_rights('write')
						move.check_access_rule('write')
						move._check_lock_date()
						self._cr.execute('UPDATE account_move '\
								   'SET state=%s '\
								   'WHERE id IN %s', ('cancel', tuple(move.ids),))
						move.invalidate_cache()
					move._check_lock_date()
				elif move.state in ('draft', 'cancel'):
					raise ValidationError('You cannot cancel Unposted,Cancel Journal Entries')
		else:
			raise ValidationError('Please tick the check-box to make sure you want to cancel')


	