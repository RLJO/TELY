# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class CustomerReportWizard(models.TransientModel):
    """
    This wizard is used to change the lock date
    """
    _name = 'customer.report.wizard'
    _description = 'Reporte de cliente individual'

    def _default_journals(self):
        return self.env['account.journal'].sudo().search([('type','=','sale')])

    partner_id = fields.Many2one('res.partner',string='Cliente', required=True)
    journal_ids = fields.Many2many('account.journal',string='Diario', required=True,
                                   default=lambda self: self.env['account.journal'].search([('type', '=', 'sale')]))


    def continue_process_report(self):

        data = {
            'journal_ids': self.journal_ids.ids,
        }
        return (self.env['ir.actions.report'].search([('report_name', '=', 'acs_customer_due.report_overdue')], limit=1).report_action(self.partner_id,data=data))


    def send_mail(self):
        self.ensure_one()

        template = self.env.ref('acs_customer_due.email_template_estado_cuenta')
        compose_form = self.env.ref('mail.email_compose_message_wizard_form')
        ctx = dict(
            default_res_id=self.partner_id.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',
            custom_layout="mail.mail_notification_light",
        )
        return {
            'name': _('Email Estado Cuenta'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }
