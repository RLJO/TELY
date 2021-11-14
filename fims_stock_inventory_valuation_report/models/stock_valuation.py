# -*- coding: utf-8 -*-
###############################################################################
#
# Fortutech IMS Pvt. Ltd.
# Copyright (C) 2016-TODAY Fortutech IMS Pvt. Ltd.(<http://www.fortutechims.com>).
#
###############################################################################

from odoo import fields, models, api, _
from openerp.tools.misc import xlwt
from io import BytesIO
import base64
    
class StockValuationReport(models.TransientModel):
    _name = 'stock.valuation.report'
    _description = "Stock Valuation Report"

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    warehourse_ids = fields.Many2many('stock.warehouse', string="Warehouse")
    location_ids = fields.Many2many('stock.location', string="Location")
    start_date = fields.Date('Start Date', default=lambda self: self._context.get('date', fields.Date.context_today(self)))
    end_date = fields.Date('End Date')
    category_ids = fields.Many2many('product.category', string="Product Category")
    
    stock_report_file = fields.Binary('Valuation Report')
    file_name = fields.Char('File Name')
    valuation_printed = fields.Boolean('Valuation Report Printed')

    @api.multi
    def generate_pdf(self):
        return self.env.ref('fims_stock_inventory_valuation_report.action_report_stock_valuation').report_action(self)
    
    @api.multi
    def generate_excel(self):
        ctx = dict(self.env.context) or {}
        workbook = xlwt.Workbook()
        
        column_heading_style = xlwt.easyxf('font:height 200;font:bold True;')
        column_data_style = xlwt.easyxf('font:height 200;')
        
        for location in self.location_ids:
            worksheet = workbook.add_sheet(location.complete_name)
            
            worksheet.write_merge(1, 1, 1, 5, "Stock Valuation Report", xlwt.easyxf('font:height 250;align: wrap on,vert centre, horiz center;font:bold True;')) 
            
            worksheet.write(4, 1, "Company", column_heading_style) 
            worksheet.write(4, 2, "Warehouse", column_heading_style) 
            worksheet.write(4, 3, "Location", column_heading_style)
            worksheet.write(4, 4, "Duration", column_heading_style)
            worksheet.write(4, 5, "Currency", column_heading_style)
            
            warehouse_name = ''
            for warehouse in self.warehourse_ids:
                warehouse_name += warehouse.name + " "
            worksheet.write(5, 1, self.company_id.name, column_data_style) 
            worksheet.write(5, 2, warehouse_name, column_data_style) 
            worksheet.write(5, 3, location.complete_name, column_data_style)
            worksheet.write(5, 4, str(self.start_date) + " to " + str(self.end_date), column_data_style)
            worksheet.write(5, 5, self.company_id.currency_id.name, column_data_style)
            
            worksheet.write(8, 0, "Default Code", column_heading_style) 
            worksheet.write(8, 1, "Name", column_heading_style) 
            worksheet.write(8, 2, "Category", column_heading_style)
            worksheet.write(8, 3, "Cost Price", column_heading_style)
            worksheet.write(8, 4, "Beginning", column_heading_style)
            worksheet.write(8, 5, "Internal", column_heading_style) 
            worksheet.write(8, 6, "Purchased", column_heading_style) 
            worksheet.write(8, 7, "Sales", column_heading_style)
            worksheet.write(8, 8, "Adjustment", column_heading_style)
            worksheet.write(8, 9, "Ending", column_heading_style)
            worksheet.write(8, 10, "Valuation", column_heading_style)
            
            i = 9
            for data in self._get_stock_valuation(self, location):
                worksheet.write(i, 0, data.get('code') or '')
                worksheet.write(i, 1, data.get('name'))
                worksheet.write(i, 2, data.get('category'))
                worksheet.write(i, 3, data.get('cost_price'))
                worksheet.write(i, 4, data.get('begining'))
                worksheet.write(i, 5, data.get('internal'))
                worksheet.write(i, 6, data.get('purchase'))
                worksheet.write(i, 7, data.get('sales'))
                worksheet.write(i, 8, data.get('adjustment'))
                worksheet.write(i, 9, data.get('ending'))
                worksheet.write(i, 10, data.get('stock_value'))
                
                i +=1

        fp = BytesIO()
        workbook.save(fp)
        excel_file = base64.encodestring(fp.getvalue())
        self.stock_report_file = excel_file
        self.file_name = 'Stock Valuation Report.xls'
        self.valuation_printed = True
        fp.close()
        return {
                'view_mode': 'form',
                'res_id': self.id,
                'res_model': 'stock.valuation.report',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'context': self.env.context,
                'target': 'new',
        } 
        
    @api.multi
    def _get_stock_valuation(self, obj, location_id):
        StockMove = self.env['stock.move']
        to_date = self.env.context.get('to_date')
        domain = [('type', '!=', 'service')]
        if obj.category_ids:
            domain.append(('categ_id', 'in', obj.category_ids.ids))
        all_product = self.env['product.product'].search(domain)
        
        real_time_product_ids = [product.id for product in all_product if product.product_tmpl_id.valuation == 'real_time']
        if real_time_product_ids:
            self.env['account.move.line'].check_access_rights('read')
            fifo_automated_values = {}
            query = """SELECT aml.product_id, aml.account_id, sum(aml.debit) - sum(aml.credit), sum(quantity), array_agg(aml.id)
                         FROM account_move_line AS aml
                        WHERE aml.product_id IN %%s AND aml.company_id=%%s %s
                     GROUP BY aml.product_id, aml.account_id"""
            params = (tuple(real_time_product_ids), self.env.user.company_id.id)
            if to_date:
                query = query % ('AND aml.date <= %s',)
                params = params + (to_date,)
            else:
                query = query % ('',)
            self.env.cr.execute(query, params=params)

            res = self.env.cr.fetchall()
            for row in res:
                fifo_automated_values[(row[0], row[1])] = (row[2], row[3], list(row[4]))

        product_values = {product: 0 for product in all_product}
            
        data = []
        for product in all_product:
            dict = {}
            begining = ending = total_adjustment = total_purchase = total_internal = total_sale = 0.0
            dict['code'] = product.default_code
            dict['name'] = product.name
            dict['category'] = product.categ_id.name
            dict['cost_price'] = product.standard_price
            
            domain = [('product_id', 'in', [product.id]), ('state', '=', 'done'), ('date', '<=', obj.end_date), ('date', '>=', obj.start_date), ('location_dest_id', '=', location_id.id)] #+ StockMove._get_all_base_domain()
            for move in StockMove.search(domain).with_context(prefetch_fields=False):
                product_values[move.product_id] += move.value
                
                #add total sales
                if move.picking_type_id and move.picking_type_id.code == 'outgoing':
                    total_sale += move.product_uom_qty
                    for return_move in move.move_dest_ids:
                        total_sale -= return_move.product_uom_qty
                #add total purchase
                if move.picking_type_id and move.picking_type_id.code == 'incoming' and not move.sale_line_id:
                    total_purchase += move.product_uom_qty
                    for return_move in move.move_dest_ids:
                        total_purchase -= return_move.product_uom_qty
                #add total internal stock
                if move.picking_type_id and move.picking_type_id.code == 'internal':
                    total_internal += move.product_uom_qty
                
                #add total adjustment stock
                if move.inventory_id:
                    total_adjustment += move.product_uom_qty

            #add begining value
            domain = [('product_id', 'in', [product.id]), ('state', '=', 'done'), ('date', '<=', obj.start_date), ('location_dest_id', '=', location_id.id)]
            for move in StockMove.search(domain).with_context(prefetch_fields=False):
                begining += move.product_uom_qty
                for return_move in move.move_dest_ids:
                    if return_move.date.date() <= obj.start_date:
                        begining -= return_move.product_uom_qty
                for return_move in move.move_orig_ids:
                    if return_move.date.date() <= obj.start_date:
                        begining -= return_move.product_uom_qty
                        
            #add ending value
            domain = [('product_id', 'in', [product.id]), ('state', '=', 'done'), ('date', '<=', obj.end_date), ('location_dest_id', '=', location_id.id)]
            for move in StockMove.search(domain).with_context(prefetch_fields=False):
                ending += move.product_uom_qty
                for return_move in move.move_dest_ids:
                    if return_move.date.date() <= obj.end_date:
                        ending -= return_move.product_uom_qty
                for return_move in move.move_orig_ids:
                    if return_move.date.date() <= obj.end_date:
                        ending -= return_move.product_uom_qty
                        
            dict['sales'] = total_sale
            dict['purchase'] = total_purchase
            dict['internal'] = total_internal
            dict['adjustment'] = total_adjustment
            dict['begining'] = begining
            dict['ending'] = ending        
            if product.cost_method in ['standard', 'average']:
                price_used = product.standard_price
                dict['stock_value'] = price_used * ending
            elif product.cost_method == 'fifo':
                if product.product_tmpl_id.valuation == 'manual_periodic':
                    dict['stock_value'] = product_values[product]
                elif product.product_tmpl_id.valuation == 'real_time':
                    valuation_account_id = product.categ_id.property_stock_valuation_account_id.id
                    value, quantity, aml_ids = fifo_automated_values.get((product.id, valuation_account_id)) or (0, 0, [])
                    dict['stock_value'] = product_values[product]
            data.append(dict)
        return data

