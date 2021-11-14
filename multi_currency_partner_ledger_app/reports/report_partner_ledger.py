# -*- coding: utf-8 -*-

from odoo import api, models, fields


class MultiReportPartnerLedger(models.AbstractModel):
    _name = 'report.multi_currency_partner_ledger_app.report_partnerledger'

    def _lines(self, data, partner, currency):
        domain = [('partner_id','=', partner.id),('currency_id','=', currency.id)]
        move_state = data['move_state']
        if move_state == ['posted']:
            domain +=[('state','=', 'open')]
        else:
            domain +=[('state','in', ['open','paid'])]
        account_type = data['account_type']
        if account_type == ['supplier']:
            domain +=[('partner_id.customer','=', False),('partner_id.supplier','=', True)]
        elif account_type == ['customer']:
            domain +=[('partner_id.customer','=', True),('partner_id.supplier','=', True)]
        else:
            domain +=['|', '|', '&','&','&',
                      ('partner_id.customer','=', True),('partner_id.supplier','=', False),
                      ('partner_id.customer','=', False),('partner_id.supplier','=', True),
                      ('partner_id.customer','=', True),('partner_id.supplier','=', True),
                      ]
        if data['date_from']:
            domain +=[('date_invoice', '>=', data['date_from'])]
        elif data['date_to']:
            domain +=[('date_invoice', '<=', data['date_to'])]
        else:
            if data['date_from'] and data['date_to']:
                domain +=[('date_invoice', '>=', data['date_from']),('date_invoice', '<=', data['date_to'])]

        invoice_ids = self.env['account.invoice'].search(domain)
        full_account = []
        for invoice in invoice_ids:
            company_currency = invoice.company_id.currency_id
            iml = invoice.invoice_line_move_line_get()
            iml += invoice.tax_line_move_line_get()
            diff_currency = invoice.currency_id != company_currency
            total, total_currency, iml = invoice.compute_invoice_totals(company_currency, iml)
            name = invoice.name or ''
            if invoice.payment_term_id:
                totlines = invoice.payment_term_id.with_context(currency_id=company_currency.id).compute(total, invoice.date_invoice)[0]
                res_amount_currency = total_currency
                for i, t in enumerate(totlines):
                    if invoice.currency_id != company_currency:
                        amount_currency = company_currency._convert(t[1], invoice.currency_id, invoice.company_id, invoice._get_currency_rate_date() or fields.Date.today())
                    else:
                        amount_currency = False
                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': invoice.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and invoice.currency_id.id,
                        'invoice_id': invoice.id
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': invoice.account_id.id,
                    'date_maturity': invoice.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and invoice.currency_id.id,
                    'invoice_id': invoice.id
                })
            line = [(invoice.line_get_convert(l, partner.id)) for l in iml]
            line = invoice.group_lines(iml, line)
            lines = invoice.finalize_invoice_move_lines(line)
            
            if invoice.move_id.name:
                displayed_name = invoice.move_id.name
            if invoice.move_id.name and invoice.reference:
                displayed_name = str(invoice.move_id.x_consec)
            debit_amount = 0.0
            for line in lines:
                amount_currency = invoice.company_id.currency_id._convert(line['debit'], invoice.currency_id, invoice.company_id, invoice.date_invoice or fields.Date.today())
                debit_amount += amount_currency
            vals = {
                'debit' : debit_amount,
                'credit' : invoice.residual,
                'progress': debit_amount - invoice.residual,
                'date': invoice.date_invoice,
                'date_due': invoice.date_due,
                'code' : invoice.journal_id.code,
                'a_code' : invoice.account_id.code,
                'displayed_name': displayed_name,
                'currency_id': invoice.currency_id.symbol,
                'invoice_id': invoice.id
            }
            full_account.append(vals)
        return full_account

    def _sum_partner(self, data, partner, currencys):
        total_credit = 0.0
        total_debit = 0.0
        total_balance = 0.0
        total_amount_lst = []
        for currency in currencys:
            records = self._lines(data, partner, currency)
            for record in records:
                total_credit += record['credit']
                total_debit  += record['debit']
                total_balance  += record['progress']
        total_amount_lst.append({'total_credit': total_credit,
                                 'total_debit': total_debit,
                                 'total_balance': total_balance})
        return total_amount_lst

    @api.model
    def _get_report_values(self, docids, data=None):
        context = data.get('context')
        currency_ids = self.env['res.currency'].browse(context.get('currency_ids'))
        partner_ids = self.env['res.partner'].browse(data.get('docs'))
        return {
            'currency_ids': currency_ids,
            'doc_model': self.env['res.partner'],
            'docs': partner_ids,
            'lines': self._lines,
            'extra': data,
            'sum_partner': self._sum_partner,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: