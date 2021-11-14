# -*- coding: utf-8 -*-

import time
from odoo import api, fields, models


class ACSReportOverdue(models.AbstractModel):
    _name = 'report.acs_customer_due.report_overdue'
    _description = "Customer Overdue Report"

    def _get_account_move_lines(self, partner_ids, data):

        res = {x: [] for x in partner_ids}
        journal_ids = False
        if 'journal_ids' in data:
            if len(data['journal_ids']) > 1 :
                journal_ids = tuple(data['journal_ids'])
            else:
                journal_ids = '(' + str(data['journal_ids'][0]) + ')'


        if partner_ids:
            if len(partner_ids) > 1:
                partner_ids = tuple(partner_ids)
            else:
                partner_ids = '(' + str(partner_ids[0]) + ')'



        sql = """ 
            SELECT
            m.name AS move_id,
            ai.sequence as consecutivo ,
            l.date,
            l.name,
            l.ref, 
            l.date_maturity,
            l.partner_id,
            l.blocked,
            l.amount_currency, 
            l.currency_id,
            CASE WHEN at.type = 'receivable' THEN SUM(l.debit) ELSE SUM(l.credit * -1) END AS debit,
            CASE WHEN at.type = 'receivable'  THEN SUM(l.credit) ELSE SUM(l.debit * -1) END AS credit,
            CASE WHEN l.date_maturity < '{0}' THEN SUM(l.debit - l.credit) ELSE 0 END AS mat
            FROM account_move_line l 
            JOIN account_account_type at ON (l.user_type_id = at.id)
            JOIN account_move m ON (l.move_id = m.id)
            LEFT JOIN account_invoice ai ON (m.id = ai.move_id)
            WHERE l.partner_id IN {1} AND at.type IN ('receivable', 'payable') AND NOT l.reconciled""".format(fields.date.today(),partner_ids)
        if journal_ids:
            sql += " and m.journal_id in {0}".format(journal_ids)
        sql += " GROUP BY l.date, l.name, l.ref, l.date_maturity, l.partner_id, at.type, l.blocked, l.amount_currency, l.currency_id, l.move_id, m.name, ai.sequence"

        self.env.cr.execute(sql)
        for row in self.env.cr.dictfetchall():
            res[row.pop('partner_id')].append(row)
        return res

    @api.model
    def _get_report_values(self, docids, data=None):       
        totals = {}
        if docids is  None:
            docids =  data['context']['active_ids']
        lines = self._get_account_move_lines(docids, data)
        lines_to_display = {}
        company_currency = self.env.user.company_id.currency_id
        for partner_id in docids:
            lines_to_display[partner_id] = {}
            totals[partner_id] = {}
            for line_tmp in lines[partner_id]:
                line = line_tmp.copy()
                currency = line['currency_id'] and self.env['res.currency'].browse(line['currency_id']) or company_currency
                if currency not in lines_to_display[partner_id]:
                    lines_to_display[partner_id][currency] = []
                    totals[partner_id][currency] = dict((fn, 0.0) for fn in ['due', 'paid', 'mat', 'total'])
                if line['debit'] and line['currency_id']:
                    line['debit'] = line['amount_currency']
                if line['credit'] and line['currency_id']:
                    line['credit'] = line['amount_currency']
                if line['mat'] and line['currency_id']:
                    line['mat'] = line['amount_currency']
                lines_to_display[partner_id][currency].append(line)
                if not line['blocked']:
                    totals[partner_id][currency]['due'] += line['debit']
                    totals[partner_id][currency]['paid'] += line['credit']
                    totals[partner_id][currency]['mat'] += line['mat']
                    totals[partner_id][currency]['total'] += line['debit'] - line['credit']

        return {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': self.env['res.partner'].browse(docids),
            'time': time,
            'Lines': lines_to_display,
            'Totals': totals,
            'Date': fields.date.today(),
        }
