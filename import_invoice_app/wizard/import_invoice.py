# -*- coding: utf-8 -*-
from odoo.exceptions import Warning, UserError
from odoo import models, fields, exceptions, api, _
import io
import tempfile
import binascii
import logging
from datetime import datetime, timedelta
from odoo.tools import pycompat

_logger = logging.getLogger(__name__)

try:
	import csv
except ImportError:
	_logger.debug('Cannot `import csv`.')
try:
	import xlwt
except ImportError:
	_logger.debug('Cannot `import xlwt`.')
try:
	import base64
except ImportError:
	_logger.debug('Cannot `import base64`.')
# for xls 
try:
	import xlrd
except ImportError:
	_logger.debug('Cannot `import xlrd`.')


from odoo import api, fields, models, _

class Stock_Import(models.TransientModel):
	_name = 'import.invoice'
	_description  =" Import Invoice"

	import_with_analytic = fields.Boolean(string='Import With Analytic Account')
	invoice_line_account = fields.Selection([('product','Use From Product'),('file','Use From File')],string="Invoice Line Account",default='product')
	file_seq = fields.Selection([('default','Use Default Sequence'),('file','Use Sequence From File')],string='Sequence Option ',default='default')
	customer_option = fields.Selection([('name', 'Name'),('ref', 'Internal Reference '),('external','External ID')],string='Search Customer ',default='name')
	invoice_option = fields.Selection([('customer', 'Customer Invoice'),('vendor', 'Vendor Bill'),('cus_refund','Customer Refund'),('ven_refund','Vendor Refund')],string='Invoice Option ',default='customer')
	import_prod_option = fields.Selection([('name', 'Name'),('barcode', 'Barcode'),('ref', 'Internal Reference '),('external','External ID')],string='Search Product',default='name')
	file_type = fields.Selection([('csv','CSV'),('xls','XLS')],default='xls',string="Type",required=True)
	import_file = fields.Binary('Select File',required=True)
	invoice_state = fields.Selection([('draft','Draft'),('validate','Validate Invoice')],string="Invoice State",default='draft')
	skip_validation = fields.Selection([('skip','Skip Validation'),('restrict','Restrict With Validation')],default="skip")
	file_name = fields.Char(string="File Name")


	def import_file_button(self):
		file_name = str(self.file_name)
		ext = ['csv','xls', 'xlsx']
		extension = file_name.split('.')[1]
		if extension not in ext or extension not in ext:
			raise UserError(_('Please upload only xls, xlsx  or csv file...!'))

		if self.invoice_option == 'customer':
			type_invoice = 'out_invoice'

		if self.invoice_option == 'vendor':
			type_invoice = 'in_invoice'

		if self.invoice_option == 'cus_refund':
			type_invoice = 'out_refund'

		if self.invoice_option == 'ven_refund':
			type_invoice = 'in_refund'
		flag = False
		validate_res = self.env['import.validation'].create({'name' : 'validate'})
		invoice_obj = self.env['account.invoice']
		account_obj = self.env['account.account']
		invoice_line_obj = self.env['account.invoice.line']
		company_id = self.env['res.users'].browse(self._context.get('uid')).company_id
		if self.file_type == 'xls' :

			if extension !=  'xls' and extension !=  'xlsx':
				raise UserError(_('Please upload xls or xlsx file...!'))
			if self.import_with_analytic:
				if file_name != "analytic_account_example.xls":
					raise UserError(_("Please upload (analytic_account_example.xls) ...!"))

			fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
			fp.write(binascii.a2b_base64(self.import_file))
			fp.seek(0)
			values = {}
			workbook = xlrd.open_workbook(fp.name)
			sheet = workbook.sheet_by_index(0)
			warning = False
			product = self.env['product.product']
			for no in range(sheet.nrows):
				if no <= 0:
					fields = map(lambda row:row.value.encode('utf-8'), sheet.row(no))
				else :
					data = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(no)))
					if self.import_with_analytic == True:
						values.update({'invoice':data[0],'customer':data[1],'delivery':data[2],'payment':data[3],'date':data[4],
								'sales_person':data[5],'sales_team':data[6],'journal' : data[7],'fiscal_potion':data[8],'product':data[9],
								'description':data[10],'account':data[11],'qty':data[12],
								'uom':data[13],'price':data[14],'tax':data[15],'analytic_account':data[16],'analytic_tags':data[17]})

					else :
						values.update({'invoice':data[0],'customer':data[1],'delivery':data[2],'payment':data[3],'date':data[4],
								'sales_person':data[5],'sales_team':data[6],'journal' : data[7],'fiscal_potion':data[8],'product':data[9],
								'description':data[10],'account':data[11],'qty':data[12],
								'uom':data[13],'price':data[14],'tax':data[15]})

					if data :
						partner_res = False
						if self.customer_option == 'name':
							partner_res = self.env['res.partner'].search([('name','=',values['customer'])],limit=1)

						if self.customer_option == 'ref':
							partner_res = self.env['res.partner'].search([('ref','=',values['customer'])],limit=1)

						if self.customer_option == 'external':
							try :
								partner_res = self.env.ref(values['customer'])
							except :
								if self.skip_validation == 'skip' :
									warning = True
									self.env['import.validation.line'].create({'element' : values['customer'] + ' is not external id.','validation_id' : validate_res.id})

								else :
									raise Warning(_('"%s" is not an external id.')%(values['customer']))

						if not partner_res :
							if self.skip_validation == 'skip' :
								warning = True
								self.env['import.validation.line'].create({'element' : values['customer'] + ' is not available.','validation_id' : validate_res.id})
							else :
								raise Warning(_('"%s" is not available.')%(values['customer']))

						journal_res = False
						journal_res = self.env['account.journal'].search([('name','=',values['journal'])],limit=1)
						if not journal_res :
							if self.skip_validation == 'skip' :
								warning = True
								self.env['import.validation.line'].create({'element' : values['journal'] + ' journal is not available.','validation_id' : validate_res.id})
							else :
								raise Warning(_('"%s"journal is not available.')%(values['journal']))

						delivery_res = False
						delivery_res = self.env['res.partner'].search([('name','=',values['delivery'])],limit=1)
						if not delivery_res :
							if self.skip_validation == 'skip' :
								warning = True
								self.env['import.validation.line'].create({'element' : values['delivery'] + ' delivery is not available.','validation_id' : validate_res.id})
							else :
								raise Warning(_('"%s"delivery is not available.')%(values['delivery']))

						payment_res = False
						payment_res = self.env['account.payment.term'].search([('name','=',values['payment'])],limit=1)
						if not payment_res :
							if self.skip_validation == 'skip' :
								warning = True
								self.env['import.validation.line'].create({'element' : values['payment'] + ' payment term is not available.','validation_id' : validate_res.id})
							else :
								raise Warning(_('"%s"payment term is not available.')%(values['payment']))

						DATETIME_FORMAT = '%d/%m/%Y'
						if isinstance(values['date'], pycompat.string_types):
							value_date = datetime.strptime(values['date'], '%m/%d/%Y').date()
							invoic_date = value_date
						else:
							value_date_int = int(float(values['date']))
							a1_as_datetime = datetime(*xlrd.xldate_as_tuple(value_date_int, workbook.datemode))
							invoic_date = a1_as_datetime.date().strftime('%m/%d/%Y')

						sales_person_res = False
						sales_team_res = False
						fiscal_potion_res =False

						if values.get('sales_person') :
							sales_person_res = self.env['res.users'].search([('name','=',values['sales_person'])],limit=1)
							if not sales_person_res :
								if self.skip_validation == 'skip' :
									warning = True
									self.env['import.validation.line'].create({'element' : values['sales_person'] + ' sales person is not available','validation_id' : validate_res.id})
								else :
									raise Warning(_('"%s"sales person is not available.')%(values['sales_person']))

						if values.get('sales_team') :
							sales_team_res = self.env['crm.team'].search([('name','=',values['sales_team'])])
							if not sales_team_res :
								if self.skip_validation == 'skip' :
									warning = True
									self.env['import.validation.line'].create({'element' : values['sales_team'] + ' sales team is not available','validation_id' : validate_res.id})
								else :
									raise Warning(_('"%s"sales team is not available.')%(values['sales_team']))

						if values.get('fiscal_potion') :
							fiscal_potion_res = self.env['account.fiscal.position'].search([('name','=',values['fiscal_potion'])])
							if not fiscal_potion_res :
								if self.skip_validation == 'skip' :
									warning = True
									self.env['import.validation.line'].create({'element' : values['fiscal_potion'] + ' fiscal position is not available.','validation_id' : validate_res.id})
								else :
									raise Warning(_('"%s"fiscal position is not available.')%(values['fiscal_potion']))

						invoice_res = False
						product_rec = False

						if self.import_prod_option == 'name' :
							product_rec = product.search([('name', '=', values['product'])],limit=1)
							if not product_rec :
								if self.skip_validation == 'skip' :
									warning = True
									self.env['import.validation.line'].create({'element' : values['product'] + ' Product is not available.','validation_id' : validate_res.id})
								else :
									raise Warning(_('"%s" Product is not available.')%(values['product']))

						if self.import_prod_option == 'barcode':
							product_rec = product.search([('barcode', '=', values['product'])],limit=1)
							if not product_rec :
								if self.skip_validation == 'skip' :
									warning = True
									self.env['import.validation.line'].create({'element' : values['product'] + ' Product is not available for this barcode.','validation_id' : validate_res.id})
								else :
									raise Warning(_('"%s" Product is not available for this barcode.')%(values['product']))

						if self.import_prod_option == 'ref':
							product_rec = product.search([('default_code', '=', values['product'])],limit=1)
							if not product_rec :
								if self.skip_validation == 'skip' :
									warning = True
									self.env['import.validation.line'].create({'element' : values['product'] + ' Product is not available for this internal reference .','validation_id' : validate_res.id})
								else :
									raise Warning(_('"%s" Product is not available for this internal reference  .')%(values['product']))

						if self.import_prod_option == 'external':
							try:
								product_rec = self.env.ref(values['product'])
							except :
								if self.skip_validation == 'skip' :
									warning = True
									self.env['import.validation.line'].create({'element' : values['product'] + ' Product is not available for this internal this external id .','validation_id' : validate_res.id})
								else :
									raise  Warning(_('"%s" Product is not available for this external id.')%(values['product']))

						if self.invoice_line_account == 'product':
							account_res = False
							if self.invoice_option == 'customer':
								if product_rec:
									account_res = product_rec.property_account_income_id or product_rec.categ_id.property_account_income_categ_id

							if self.invoice_option == 'vendor':
								if product_rec:
									account_res = product_rec.property_account_expense_id or product_rec.categ_id.property_account_expense_categ_id

							if self.invoice_option == 'cus_refund':
								if product_rec:
									account_res = product_rec.property_account_income_id or product_rec.categ_id.property_account_income_categ_id

							if self.invoice_option == 'ven_refund':
								if product_rec:
									account_res = product_rec.property_account_expense_id or product_rec.categ_id.property_account_expense_categ_id

						if self.invoice_line_account == 'file':
							account_res = account_obj.search([('name','=',values['account'])])
							if not account_res :
								if self.skip_validation == 'skip' :
									warning = True
									self.env['import.validation.line'].create({'element' : values['account'] + ' Account is not available .','validation_id' : validate_res.id})
								else :
									raise Warning(_('"%s" Account is not available .')%(values['account']))

						uom_rec = self.env['uom.uom'].search([('name','=',values['uom'])],limit=1)
						if not uom_rec :
							if self.skip_validation == 'skip' :
									warning = True
									self.env['import.validation.line'].create({'element' : values['uom'] + ' Uom is not available.','validation_id' : validate_res.id})
							else :
								raise Warning(_('"%s" Uom is not available.')%(values['uom']))

						tags_list = []
						if self.import_with_analytic == True :
							analytic_account_res = self.env['account.analytic.account'].search([('name','=',values.get('analytic_account'))])
							if not analytic_account_res :
								if self.skip_validation == 'skip' :
									warning = True
									self.env['import.validation.line'].create({'element' : values['account'] + ' Analytic Account is not available .','validation_id' : validate_res.id})
								else :
									raise Warning(_('"%s"Analytic Account is not available .')%(values['account']))

							tags_list = []
							if values.get('analytic_tags') :
								if ';' in  values.get('analytic_tags'):
									tag_names = values.get('analytic_tags').split(';')
									for name in tag_names:
										tag= self.env['account.analytic.tag'].search([('name', '=', name)])
										if not tag:
											if self.skip_validation == 'skip' :
												warning = True
												self.env['import.validation.line'].create({'element' : name + ' Tag not in your system .','validation_id' : validate_res.id})
											else :
												raise Warning(_('"%s" Tag not in your system') % name)
										tags_list.append(tag.id)

								elif ',' in  values.get('analytic_tags'):
									tag_names = values.get('analytic_tags').split(',')
									for name in tag_names:
										tag= self.env['account.analytic.tag'].search([('name', '=', name)])
										if not tag:
											if self.skip_validation == 'skip' :
												warning = True
												self.env['import.validation.line'].create({'element' : name + ' Tag not in your system .','validation_id' : validate_res.id})
											else :
												raise Warning(_('"%s" Tag not in your system') % name)
										tags_list.append(tag.id)

								else:
									tag_names = values.get('analytic_tags').split(',')
									for name in tag_names:
										tag= self.env['account.analytic.tag'].search([('name', '=', name)])
										if not tag:
											if self.skip_validation == 'skip' :
												warning = True
												self.env['import.validation.line'].create({'element' : name + ' Tag not in your system .','validation_id' : validate_res.id})

											else :
												raise Warning(_('"%s" Tag not in your system') % name)
										tags_list.append(tag.id)

						tax_list = []
						if values.get('tax'):
							if ';' in  values.get('tax'):
								tax_names = values.get('tax').split(';')
								for name in tax_names:
									tax= self.env['account.tax'].search([('name', '=', name)])
									if not tax:
										if self.skip_validation == 'skip' :
											warning = True
											self.env['import.validation.line'].create({'element' : name + ' Tax not in your system .','validation_id' : validate_res.id})
										else :
											raise Warning(_('"%s" Tax not in your system') % name)
									tax_list.append(tax.id)

							elif ',' in  values.get('tax'):
								tax_names = values.get('tax').split(',')
								for name in tax_names:
									tax= self.env['account.tax'].search([('name', '=', name),('type_tax_use','=','sale')])
									if not tax:
										if self.skip_validation == 'skip' :
											warning = True
											self.env['import.validation.line'].create({'element' : name + ' Tax not in your system .','validation_id' : validate_res.id})
										else :
											raise Warning(_('"%s" Tax not in your system') % name)
									tax_list.append(tax.id)

							else:
								tax_names = values.get('tax').split(',')
								for name in tax_names:
									tax= self.env['account.tax'].search([('name', '=', name),('type_tax_use','=','sale')])
									if not tax:
										if self.skip_validation == 'skip' :
											warning = True
											self.env['import.validation.line'].create({'element' : name + ' Tax not in your system .','validation_id' : validate_res.id})

										else :
											raise Warning(_('"%s" Tax not in your system') % tax_names)
									tax_list.append(tax.id)

						if sales_person_res :
							sales_person_id = sales_person_res.id
						else :
							sales_person_id = False

						if sales_team_res :
							sales_team_id = sales_team_res.id
						else :
							sales_team_id = False

						if fiscal_potion_res :
							fiscal_potion_id = fiscal_potion_res.id
						else :
							fiscal_potion_id = False

						if warning == True :
							flag = True
							continue

						if self.file_seq == 'file' :
							new_invoice = invoice_obj.search([('new_seq', '=',
															values['invoice']),('type','=',type_invoice),('partner_id','=',partner_res.id)],limit=1)
							if not new_invoice :
								new_invoice = invoice_obj.create({'partner_id':partner_res.id,'type':type_invoice,'journal' :journal_res.id,
											'partner_shipping_id' : delivery_res.id,'payment_term_id':payment_res.id,'date_invoice':invoic_date,
											'user_id':sales_person_id ,'team_id':sales_team_id,'fiscal_potion_id':fiscal_potion_id,
											'import_seq':True,'new_seq': values['invoice']})

								if self.import_with_analytic == True:
									rec = invoice_line_obj.create({
										'product_id' : product_rec.id,
										'quantity' : values.get('qty'),
										'price_unit' : values.get('price'),
										'name' : values.get('description'),
										'account_id' : account_res.id,
										'uom_id' : uom_rec.id,
										'invoice_id' : new_invoice.id,
										'account_analytic_id':analytic_account_res.id ,
										
									})
									rec.write({'analytic_tag_ids':([(6,0,tags_list)]),
												'invoice_line_tax_ids':([(6,0,tax_list)]) })
								else :
									rec = invoice_line_obj.create({
										'product_id' : product_rec.id,
										'quantity' : values.get('qty'),
										'price_unit' : values.get('price'),
										'name' : values.get('description'),
										'account_id' : account_res.id,
										'uom_id' : uom_rec.id,
										'invoice_id' : new_invoice.id
									})
									rec.write({
												'invoice_line_tax_ids':([(6,0,tax_list)]) })

								if self.invoice_state == 'validate' :
									if new_invoice.state == 'draft' :
										new_invoice.action_invoice_open()

							else :

								if self.import_with_analytic == True:
									rec = invoice_line_obj.create({
										'product_id' : product_rec.id,
										'quantity' : values.get('qty'),
										'price_unit' : values.get('price'),
										'name' : values.get('description'),
										'account_id' : account_res.id,
										'uom_id' : uom_rec.id,
										'invoice_id' : new_invoice.id,
										'account_analytic_id':analytic_account_res.id ,
										
									})
									rec.write({'analytic_tag_ids':([(6,0,tags_list)]),
												'invoice_line_tax_ids':([(6,0,tax_list)]) })
								else :
									rec = invoice_line_obj.create({
										'product_id' : product_rec.id,
										'quantity' : values.get('qty'),
										'price_unit' : values.get('price'),
										'name' : values.get('description'),
										'account_id' : account_res.id,
										'uom_id' : uom_rec.id,
										'invoice_id' : new_invoice.id
									})
									rec.write({
												'invoice_line_tax_ids':([(6,0,tax_list)]) })

							if self.invoice_state == 'validate' :
								if new_invoice.state == 'draft' :
									new_invoice.action_invoice_open()  

						else :
							new_invoice = False
							new_invoice = invoice_obj.search([('new_seq', '=',
															values['invoice']),('type','=',type_invoice),('partner_id','=',partner_res.id)],limit=1)
							if not new_invoice :
								new_invoice  = invoice_obj.create({'partner_id':partner_res.id,'type':type_invoice,'journal' :journal_res.id,
											'partner_shipping_id' : delivery_res.id,'payment_term_id':payment_res.id,'date_invoice':invoic_date,
											'user_id':sales_person_id ,'team_id':sales_team_id,'fiscal_potion_id':fiscal_potion_id,
											'import_seq':False,'new_seq': values['invoice']
											} )

							if self.import_with_analytic == True:
								rec = invoice_line_obj.create({
									'product_id' : product_rec.id,
									'quantity' : values.get('qty'),
									'price_unit' : values.get('price'),
									'name' : values.get('description'),
									'account_id' : account_res.id,
									'uom_id' : uom_rec.id,
									'invoice_id' : new_invoice.id,
									'account_analytic_id':analytic_account_res.id ,
									'analytic_tags_ids': tags_list
								})
								rec.write({'analytic_tag_ids':([(6,0,tags_list)]),
											'invoice_line_tax_ids':([(6,0,tax_list)]) })
							else :
								rec = invoice_line_obj.create({
									'product_id' : product_rec.id,
									'quantity' : values.get('qty'),
									'price_unit' : values.get('price'),
									'name' : values.get('description'),
									'account_id' : account_res.id,
									'uom_id' : uom_rec.id,
									'invoice_id' : new_invoice.id
								})
								rec.write({
											'invoice_line_tax_ids':([(6,0,tax_list)]) })

							if self.invoice_state == 'validate' :
								if new_invoice.state == 'draft' :
									new_invoice.action_invoice_open()

		elif self.file_type == 'csv' :
			if extension !=  'csv':
				raise UserError(_('Please upload csv file...!'))

			if self.import_with_analytic:
				if file_name != "analytic_account_example.csv":
					raise UserError(_("Please upload (analytic_account_example.csv) ...!"))

			csv_data = base64.b64decode(self.import_file)
			data_file = io.StringIO(csv_data.decode("utf-8"))
			data_file.seek(0)
			file_reader = []
			csv_reader = csv.reader(data_file, delimiter=',')
			warning = False
			
			product = self.env['product.product']
			values = {}
			if self.import_with_analytic == True:
				keys = ['invoice','customer','delivery','payment','date',
								'sales_person','sales_team','journal','fiscal_potion','product',
								'description','account','qty',
								'uom','price','tax','analytic_account','analytic_tags']
			else :

				keys = ['invoice','customer','delivery','payment','date',
								'sales_person','sales_team','journal','fiscal_potion','product',
								'description','account','qty',
								'uom','price','tax']

			try:
				file_reader.extend(csv_reader)
			except Exception:
				raise exceptions.Warning(_("Invalid file!"))


			for no in range(len(file_reader)):

				if no!= 0:
					val = {}
					try:
						 field = list(map(str, file_reader[no]))
					except ValueError:
						 raise exceptions.Warning(_("Dont Use Charecter only use numbers"))
					
					values = dict(zip(keys, field))

					if values :
						partner_res = False
						if self.customer_option == 'name':

							partner_res = self.env['res.partner'].search([('name','=',values['customer'])],limit=1)
						if self.customer_option == 'ref':

							
							partner_res = self.env['res.partner'].search([('ref','=',values['customer'])],limit=1)
						
						if self.customer_option == 'external':
							try :
								partner_res = self.env.ref(values['customer'])
							except :
								if self.skip_validation == 'skip' :
									warning = True
									self.env['import.validation.line'].create({'element' : values['customer'] + ' is not external id.','validation_id' : validate_res.id})
								else :
									raise Warning(_('"%s" is not an external id.')%(values['customer']))

						if not partner_res :
							if self.skip_validation == 'skip' :
								warning = True
								self.env['import.validation.line'].create({'element' : values['customer'] + ' is not available.','validation_id' : validate_res.id})
							else :
								raise Warning(_('"%s" is not available.')%(values['customer']))

						journal_res = False
						journal_res = self.env['account.journal'].search([('name','=',values['journal'])],limit=1)
						if not journal_res :
							if self.skip_validation == 'skip' :
								warning = True
								self.env['import.validation.line'].create({'element' : values['journal'] + ' journal is not available.','validation_id' : validate_res.id})
							else :
								raise Warning(_('"%s"journal is not available.')%(values['journal']))

						delivery_res = False
						delivery_res = self.env['res.partner'].search([('name','=',values['delivery'])],limit=1)
						if not delivery_res :
							if self.skip_validation == 'skip' :
								warning = True
								self.env['import.validation.line'].create({'element' : values['delivery'] + ' delivery is not available.','validation_id' : validate_res.id})
							else :
								raise Warning(_('"%s"delivery is not available.')%(values['delivery']))

						payment_res = False
						payment_res = self.env['account.payment.term'].search([('name','=',values['payment'])],limit=1)
						if not payment_res :
							if self.skip_validation == 'skip' :
								warning = True
								self.env['import.validation.line'].create({'element' : values['payment'] + ' payment term is not available.','validation_id' : validate_res.id})
							else :
								raise Warning(_('"%s"payment term is not available.')%(values['payment']))

						DATETIME_FORMAT = '%d/%m/%Y'
						invoic_date = datetime.strptime(values['date'], '%m/%d/%Y').date()

						sales_person_res = False
						sales_team_res = False
						fiscal_potion_res =False
						if values.get('sales_person') :
							sales_person_res = self.env['res.users'].search([('name','=',values['sales_person'])],limit=1)
							if not sales_person_res :
								if self.skip_validation == 'skip' :
									warning = True
									self.env['import.validation.line'].create({'element' : values['sales_person'] + ' sales person is not available','validation_id' : validate_res.id})
								else :
									raise Warning(_('"%s"sales person is not available.')%(values['sales_person']))

						if values.get('sales_team') :
							sales_team_res = self.env['crm.team'].search([('name','=',values['sales_team'])])
							if not sales_team_res :
								if self.skip_validation == 'skip' :
									warning = True
									self.env['import.validation.line'].create({'element' : values['sales_team'] + ' sales team is not available','validation_id' : validate_res.id})
								else :
									raise Warning(_('"%s"sales team is not available.')%(values['sales_team']))

						if values.get('fiscal_potion') :
							fiscal_potion_res = self.env['account.fiscal.position'].search([('name','=',values['fiscal_potion'])])
							if not fiscal_potion_res :
								if self.skip_validation == 'skip' :
									warning = True
									self.env['import.validation.line'].create({'element' : values['fiscal_potion'] + ' fiscal position is not available.','validation_id' : validate_res.id})
								else :
									raise Warning(_('"%s"fiscal position is not available.')%(values['fiscal_potion']))

						invoice_res = False
						product_rec = False

						if self.import_prod_option == 'name' :
							product_rec = product.search([('name', '=', values['product'])],limit=1)
							if not product_rec :
								if self.skip_validation == 'skip' :
									warning = True
									self.env['import.validation.line'].create({'element' : values['product'] + ' Product is not available.','validation_id' : validate_res.id})
								else :
									raise Warning(_('"%s" Product is not available.')%(values['product']))

						if self.import_prod_option == 'barcode':
							product_rec = product.search([('barcode', '=', values['product'])],limit=1)
							if not product_rec :
								if self.skip_validation == 'skip' :
									warning = True
									self.env['import.validation.line'].create({'element' : values['product'] + ' Product is not available for this barcode.','validation_id' : validate_res.id})
								else :
									raise Warning(_('"%s" Product is not available for this barcode.')%(values['product']))

						if self.import_prod_option == 'ref':
							product_rec = product.search([('default_code', '=',values['product'])],limit=1)
							if not product_rec :
								if self.skip_validation == 'skip' :
									warning = True
									self.env['import.validation.line'].create({'element' : values['product'] + ' Product is not available for this internal reference .','validation_id' : validate_res.id})
								else :
									raise Warning(_('"%s" Product is not available for this internal reference  .')%(values['product']))

						if self.import_prod_option == 'external':
							try:
								product_rec = self.env.ref(values['product'])
							except :
								if self.skip_validation == 'skip' :
									warning = True
									self.env['import.validation.line'].create({'element' : values['product'] + ' Product is not available for this internal this external id .','validation_id' : validate_res.id})
								else :
									raise  Warning(_('"%s" Product is not available for this external id.')%(values['product']))

						if self.invoice_line_account == 'product':
							account_res = False
							if self.invoice_option == 'customer':
								if product_rec:
									account_res = product_rec.property_account_income_id or product_rec.categ_id.property_account_income_categ_id

							if self.invoice_option == 'vendor':
								if product_rec:
									account_res = product_rec.property_account_expense_id or product_rec.categ_id.property_account_expense_categ_id


							if self.invoice_option == 'cus_refund':
								if product_rec:
									account_res = product_rec.property_account_income_id or product_rec.categ_id.property_account_income_categ_id

							if self.invoice_option == 'ven_refund':
								if product_rec:
									account_res = product_rec.property_account_expense_id or product_rec.categ_id.property_account_expense_categ_id


						if self.invoice_line_account == 'file':
							account_res = account_obj.search([('name','=',values['account'])])
							if not account_res :
								if self.skip_validation == 'skip' :
									warning = True
									self.env['import.validation.line'].create({'element' : values['account'] + ' Account is not available .','validation_id' : validate_res.id})
								else :
									raise Warning(_('"%s" Account is not available .')%(values['account']))

						uom_rec = self.env['uom.uom'].search([('name','=',values['uom'])],limit=1)
						if not uom_rec :
							if self.skip_validation == 'skip' :
									warning = True
									self.env['import.validation.line'].create({'element' : values['uom'] + ' Uom is not available.','validation_id' : validate_res.id})
							else :
								raise Warning(_('"%s" Uom is not available.')%(values['uom']))

						tags_list = []
						if self.import_with_analytic == True :
							analytic_account_res = self.env['account.analytic.account'].search([('name','=',values.get('analytic_account'))])
							if not analytic_account_res :
								if self.skip_validation == 'skip' :
									warning = True
									self.env['import.validation.line'].create({'element' : values['account'] + ' Analytic Account is not available .','validation_id' : validate_res.id})
								else :
									raise Warning(_('"%s"Analytic Account is not available .')%(values['account']))

							tags_list = []
							if values.get('analytic_tags') :
								if ';' in  values.get('analytic_tags'):
									tag_names = values.get('analytic_tags').split(';')
									for name in tag_names:
										tag= self.env['account.analytic.tag'].search([('name', '=', name)])
										if not tag:
											if self.skip_validation == 'skip' :
												warning = True
												self.env['import.validation.line'].create({'element' : name + ' Tag not in your system .','validation_id' : validate_res.id})

											else :
												raise Warning(_('"%s" Tag not in your system') % name)
										tags_list.append(tag.id)

								elif ',' in  values.get('analytic_tags'):
									tag_names = values.get('analytic_tags').split(',')
									for name in tag_names:
										tag= self.env['account.analytic.tag'].search([('name', '=', name)])
										if not tag:
											if self.skip_validation == 'skip' :
												warning = True
												self.env['import.validation.line'].create({'element' : name + ' Tag not in your system .','validation_id' : validate_res.id})

											else :
												raise Warning(_('"%s" Tag not in your system') % name)
										tags_list.append(tag.id)

								else:
									tag_names = values.get('analytic_tags').split(',')
									for name in tag_names:
										tag= self.env['account.analytic.tag'].search([('name', '=', name)])
										if not tag:
											if self.skip_validation == 'skip' :
												warning = True
												self.env['import.validation.line'].create({'element' : name + ' Tag not in your system .','validation_id' : validate_res.id})
											else :
												raise Warning(_('"%s" Tag not in your system') % name)
										tags_list.append(tag.id)

						tax_list = []
						if values.get('tax'):
							if ';' in  values.get('tax'):
								tax_names = values.get('tax').split(';')
								for name in tax_names:
									tax= self.env['account.tax'].search([('name', '=', name)])
									if not tax:
										if self.skip_validation == 'skip' :
											warning = True
											self.env['import.validation.line'].create({'element' : name + ' Tax not in your system .','validation_id' : validate_res.id})

										else :
											raise Warning(_('"%s" Tax not in your system') % name)
									tax_list.append(tax.id)

							elif ',' in  values.get('tax'):
								tax_names = values.get('tax').split(',')
								for name in tax_names:
									tax= self.env['account.tax'].search([('name', '=', name),('type_tax_use','=','sale')])
									if not tax:
										if self.skip_validation == 'skip' :
											warning = True
											self.env['import.validation.line'].create({'element' : name + ' Tax not in your system .','validation_id' : validate_res.id})

										else :
											raise Warning(_('"%s" Tax not in your system') % name)
									tax_list.append(tax.id)

							else:
								tax_names = values.get('tax').split(',')
								for name in tax_names:
									tax= self.env['account.tax'].search([('name', '=', name),('type_tax_use','=','sale')])
									if not tax:
										if self.skip_validation == 'skip' :
											warning = True
											self.env['import.validation.line'].create({'element' : name + ' Tax not in your system .','validation_id' : validate_res.id})

										else :
											raise Warning(_('"%s" Tax not in your system') % tax_names)
									tax_list.append(tax.id)

						if sales_person_res :
							sales_person_id = sales_person_res.id
						else :
							sales_person_id = False

						if sales_team_res :
							sales_team_id = sales_team_res.id
						else :
							sales_team_id = False

						if fiscal_potion_res :
							fiscal_potion_id = fiscal_potion_res.id
						else :
							fiscal_potion_id = False

						if warning == True :
							flag = True
							continue

						if self.file_seq == 'file' :

							new_invoice = invoice_obj.search([('new_seq', '=',
															values['invoice']),('type','=',type_invoice),('partner_id','=',partner_res.id)],limit=1)
							if not new_invoice :
								new_invoice = invoice_obj.create({'partner_id':partner_res.id,'type':type_invoice,'journal' :journal_res.id,
											'partner_shipping_id' : delivery_res.id,'payment_term_id':payment_res.id,'date_invoice':invoic_date,
											'user_id':sales_person_id ,'team_id':sales_team_id,'fiscal_potion_id':fiscal_potion_id,
											'import_seq':True,'new_seq': values['invoice']})

								if self.import_with_analytic == True:
									rec = invoice_line_obj.create({
										'product_id' : product_rec.id,
										'quantity' : values.get('qty'),
										'price_unit' : values.get('price'),
										'name' : values.get('description'),
										'account_id' : account_res.id,
										'uom_id' : uom_rec.id,
										'invoice_id' : new_invoice.id,
										'account_analytic_id':analytic_account_res.id ,
									})
									rec.write({'analytic_tag_ids':([(6,0,tags_list)]),
												'invoice_line_tax_ids':([(6,0,tax_list)]) })
								else :
									rec = invoice_line_obj.create({
										'product_id' : product_rec.id,
										'quantity' : values.get('qty'),
										'price_unit' : values.get('price'),
										'name' : values.get('description'),
										'account_id' : account_res.id,
										'uom_id' : uom_rec.id,
										'invoice_id' : new_invoice.id
									})
									rec.write({'invoice_line_tax_ids':([(6,0,tax_list)]) })

								if self.invoice_state == 'validate' :
									if new_invoice.state == 'draft' :
										new_invoice.action_invoice_open()
							else :
								if self.import_with_analytic == True:
									rec = invoice_line_obj.create({
										'product_id' : product_rec.id,
										'quantity' : values.get('qty'),
										'price_unit' : values.get('price'),
										'name' : values.get('description'),
										'account_id' : account_res.id,
										'uom_id' : uom_rec.id,
										'invoice_id' : new_invoice.id,
										'account_analytic_id':analytic_account_res.id ,
									})
									rec.write({'analytic_tag_ids':([(6,0,tags_list)]),
												'invoice_line_tax_ids':([(6,0,tax_list)]) })
								else :
									rec = invoice_line_obj.create({
										'product_id' : product_rec.id,
										'quantity' : values.get('qty'),
										'price_unit' : values.get('price'),
										'name' : values.get('description'),
										'account_id' : account_res.id,
										'uom_id' : uom_rec.id,
										'invoice_id' : new_invoice.id
									})
									rec.write({'invoice_line_tax_ids':([(6,0,tax_list)]) })

								if self.invoice_state == 'validate' :
									if new_invoice.state == 'draft' :
										new_invoice.action_invoice_open()    
								
						else :

							new_invoice = False
							new_invoice = invoice_obj.search([('new_seq', '=',
															values['invoice']),('type','=',type_invoice),('partner_id','=',partner_res.id)],limit=1)
							if not new_invoice :
								new_invoice  = invoice_obj.create({'partner_id':partner_res.id,'type':type_invoice,'journal' :journal_res.id,
											'partner_shipping_id' : delivery_res.id,'payment_term_id':payment_res.id,'date_invoice':invoic_date,
											'user_id':sales_person_id ,'team_id':sales_team_id,'fiscal_potion_id':fiscal_potion_id,
											'import_seq':False,'new_seq': values['invoice']
											} )

							if self.import_with_analytic == True:
								rec = invoice_line_obj.create({
									'product_id' : product_rec.id,
									'quantity' : values.get('qty'),
									'price_unit' : values.get('price'),
									'name' : values.get('description'),
									'account_id' : account_res.id,
									'uom_id' : uom_rec.id,
									'invoice_id' : new_invoice.id,
									'account_analytic_id':analytic_account_res.id ,
									'analytic_tags_ids': tags_list
								})
								rec.write({'analytic_tag_ids':([(6,0,tags_list)]),
											'invoice_line_tax_ids':([(6,0,tax_list)]) })
							else :
								rec = invoice_line_obj.create({
									'product_id' : product_rec.id,
									'quantity' : values.get('qty'),
									'price_unit' : values.get('price'),
									'name' : values.get('description'),
									'account_id' : account_res.id,
									'uom_id' : uom_rec.id,
									'invoice_id' : new_invoice.id
								})
								rec.write({'invoice_line_tax_ids':([(6,0,tax_list)]) })

							if self.invoice_state == 'validate' :
								if new_invoice.state == 'draft' :
									new_invoice.action_invoice_open()

		if flag == True :
			return {
							'view_mode': 'form',
							'res_id': validate_res.id,
							'res_model': 'import.validation',
							'view_type': 'form',
							'type': 'ir.actions.act_window',
							'target':'new'
					}