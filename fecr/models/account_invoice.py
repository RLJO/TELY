# -*- coding: utf-8 -*-
import base64
import datetime
import json
import logging
import re
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import email_escape_char, email_re, email_split

from . import api_facturae

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    number_electronic = fields.Char(
        copy=False,
        index=True,string='Número Electrónico'
    )
    date_issuance = fields.Char(
        copy=False, string=u'Fecha Emisión'
    )
    consecutive_number_receiver = fields.Char(
        copy=False,
        readonly=True,
        index=True,
    )
    state_send_invoice = fields.Selection(
        selection=[
            ("aceptado", _("Aceptado")),
            ("rechazado", _("Rechazado")),
            ("error", "Error"),
            ("na", _("No Aplica")),
            ("ne", _("No Econtrado")),
            ("firma_invalida", u'Firma Inválida'),
            ("procesando", _("Procesando")),
        ],string='Estado al enviar el comprobante'
    )
    state_tributacion = fields.Selection(
        selection=[
            ("aceptado", _("Aceptado")),
            ("rechazado", _("Rechazado")),
            ("recibido", _("Recibido")),
            ("firma_invalida", _("Firma Inválida")),
            ("error", "Error"),
            ("procesando", _("Procesando")),
            ("na", _("No Aplicado")),
            ("ne", _("No Econtrado")),
        ],
        copy=False, string='Hacienda Estado'
    )
    state_invoice_partner = fields.Selection(
        selection=[
            ("1", _("Aceptado")),
            ("3", _("Rechazado")),
            ("2", _("Aceptado Parcialmente")),
        ],string='Acepta este comprobante ? '
    )
    reference_code_id = fields.Many2one(
        comodel_name="reference.code",
    )
    # payment_methods_id = fields.Many2one(
    #     comodel_name="payment.methods", string=u'Método de pago',
    # )
    payment_methods_id = fields.Many2one('payment.methods', string=u'Método de pago',store=True,related='partner_id.payment_methods_id',related_sudo=False)
    invoice_id = fields.Many2one(
        comodel_name="account.invoice",
        string="Reference",
        copy=False,
    )
    xml_respuesta_tributacion = fields.Binary(
        copy=False,
        attachment=True, string='Respuesta Hacienda .XML'
    )
    electronic_invoice_return_message = fields.Text(
        copy=False,
        readonly=True,
    )
    fname_xml_respuesta_tributacion = fields.Char(
        copy=False,
    )
    xml_comprobante = fields.Binary(
        copy=False,
        attachment=True,
    )
    fname_xml_comprobante = fields.Char(
        copy=False,
        attachment=True,
    )
    xml_supplier_approval = fields.Binary(
        copy=False,
        attachment=True,string='Aprobación Proveedor .XML'
    )
    fname_xml_supplier_approval = fields.Char(
        copy=False,
        attachment=True,
    )
    amount_tax_electronic_invoice = fields.Monetary(
        readonly=True,
    )
    amount_total_electronic_invoice = fields.Monetary(
        readonly=True,
    )
    tipo_documento = fields.Selection(
        selection=[
            ("FE", _("Electronic Bill")),
            ("FEE", _("Electronic Export Invoice")),
            ("TE", _("Electronic Ticket")),
            ("NC", _("Credit Note")),
            ("ND", _("Debit Note")),
            ("CCE", _("MR Acceptance")),
            ("CPCE", _("MR Partial Acceptance")),
            ("RCE", _("MR Rejection")),
            ("FEC", _("Electronic Export Invoice")),
        ],
        default="FE",
        help="Indicates the type of document according to the classification of the Ministry of Finance",
    )
    sequence = fields.Char(
        readonly=True,
        copy=False,
        store=True
    )
    state_email = fields.Selection(
        selection=[
            ("no_email", _("No email account")),
            ("sent", _("Sent")),
            ("fe_error", _("Error FE")),
        ],
        copy=False,
    )
    invoice_amount_text = fields.Char(
        compute="_compute_invoice_amount_text",
    )
    ignore_total_difference = fields.Boolean(
        default=False,
    )
    error_count = fields.Integer(
        default="0",
    )
    activity_id = fields.Many2one(
        comodel_name="economic_activity",
        ondelete="restrict",
        required=True,
        default=lambda self: self.env.user.company_id.activity_id
        and self.env.user.company_id.activity_id[0],
        domain=lambda self: [("id", "in", self.env.user.company_id.activity_id.ids)],
    )
    total_services_taxed = fields.Float(
        compute="_compute_total_services_taxed",
    )
    total_services_exempt = fields.Float(
        compute="_compute_total_services_exempt",
    )
    total_products_taxed = fields.Float(
        compute="_compute_total_products_taxed",
    )
    total_products_exempt = fields.Float(
        compute="_compute_total_products_exempt",
    )
    total_taxed = fields.Float(
        compute="_compute_total_taxed",
    )
    total_exempt = fields.Float(
        compute="_compute_total_exempt",
    )
    total_sale = fields.Float(
        compute="_compute_total_sale",
    )
    total_discount = fields.Float(
        compute="_compute_total_discount",
    )
    total_others = fields.Float(
        compute="_compute_total_others",
    )
    purchase_type = fields.Selection(
        selection=[
            ("purchase", _("Purchase")),
            ("asset", _("Asset")),
            ("service", _("Service")),
            ("no_subject", _("No subject")),
        ],
    )
    usd_rate = fields.Float(
        compute="_compute_usd_currency_id",
    )

    _sql_constraints = [
        (
            "number_electronic_uniq",
            "UNIQUE(company_id, number_electronic)",
            "La clave de comprobante debe ser única",
        ),
    ]
    to_process = fields.Boolean(
        compute="_compute_to_process",
    )

    # Todo Nuevo 08-11-21
    sur_quimica_data_add = fields.Boolean()
    sur_quimica_number = fields.Char(string=u'Número')
    sur_quimica_reason = fields.Char(string=u'Razón')

    @api.model
    def default_get(self, fields):
        values = super(AccountInvoice, self).default_get(fields)
        einvoice_fields_add = bool(self.env["ir.config_parameter"].sudo().get_param("einvoice_fields_add"))
        values['sur_quimica_data_add'] = einvoice_fields_add
        return values


    @api.depends("company_id.frm_ws_ambiente", "journal_id.to_process")
    def _compute_to_process(self):
        for invoice in self:
            invoice.to_process = (
                invoice.company_id.frm_ws_ambiente != "disabled" and invoice.journal_id.to_process
            )

    @api.depends("date_invoice", "company_id.currency_id")
    def _compute_usd_currency_id(self):
        for record in self:
            if record.date_invoice:
                record.usd_rate = self.env.ref("base.USD")._convert(
                    1, record.company_id.currency_id, record.company_id, record.date_invoice
                )

    @api.depends("invoice_line_ids")
    def _compute_total_services_taxed(self):
        for record in self:
            record.total_services_taxed = sum(
                record.invoice_line_ids.filtered(
                    lambda l: l.product_id.type == "service" and l.invoice_line_tax_ids
                ).mapped("price_subtotal")
            )

    @api.depends("invoice_line_ids")
    def _compute_total_services_exempt(self):
        for record in self:
            record.total_services_exempt = sum(
                record.invoice_line_ids.filtered(
                    lambda l: l.product_id.type == "service" and not l.invoice_line_tax_ids
                ).mapped("price_subtotal")
            )

    @api.depends("invoice_line_ids")
    def _compute_total_products_taxed(self):
        for record in self:
            record.total_products_taxed = sum(
                record.invoice_line_ids.filtered(
                    lambda l: l.product_id.type != "service" and l.invoice_line_tax_ids
                ).mapped("price_subtotal")
            )

    @api.depends("invoice_line_ids")
    def _compute_total_products_exempt(self):
        for record in self:
            record.total_products_exempt = sum(
                record.invoice_line_ids.filtered(
                    lambda l: l.product_id.type != "service" and not l.invoice_line_tax_ids
                ).mapped("price_subtotal")
            )

    @api.depends("total_products_taxed", "total_services_taxed")
    def _compute_total_taxed(self):
        for record in self:
            record.total_taxed = record.total_products_taxed + record.total_services_taxed

    @api.depends("total_products_exempt", "total_services_exempt")
    def _compute_total_exempt(self):
        for record in self:
            record.total_exempt = record.total_products_exempt + record.total_services_exempt

    @api.depends("total_products_taxed", "total_services_taxed")
    def _compute_total_sale(self):
        for record in self:
            record.total_sale = record.total_taxed + record.total_exempt

    def _compute_total_discount(self):
        for record in self:
            record.total_discount = sum(record.invoice_line_ids.mapped("discount_amount"))

    def _compute_total_others(self):
        for record in self:
            record.total_others = 0  # TODO

    def name_get(self):
        """
        - Add amount_untaxed in name_get of invoices
        - Skipp number usage on invoice from incoming mail
        """
        if self._context.get("invoice_from_incoming_mail"):
            logging.info("Factura de correo")
            res = []
            for inv in self:
                res.append((inv.id, (inv.name or str(inv.id)) + "MI"))
            return res
        res = super(AccountInvoice, self).name_get()
        if self._context.get("invoice_show_amount"):
            new_res = []
            for (inv_id, name) in res:
                inv = self.browse(inv_id)
                name += _(" Amount w/o tax: {} {}").format(inv.amount_untaxed, inv.currency_id.name)
                new_res.append((inv_id, name))
            return new_res
        else:
            return res

    @api.depends("amount_total")
    def _compute_invoice_amount_text(self):
        for record in self:
            record.invoice_amount_text = record.currency_id.amount_to_text(record.amount_total)

    def action_invoice_sent(self):
        pass

    @api.onchange("xml_supplier_approval")
    def _onchange_xml_supplier_approval(self):
        if not self.xml_supplier_approval:
            self.state_tributacion = False
            self.state_send_invoice = False
            self.xml_supplier_approval = False
            self.fname_xml_supplier_approval = False
            self.xml_respuesta_tributacion = False
            self.fname_xml_respuesta_tributacion = False
            self.date_issuance = False
            self.number_electronic = False
            self.state_invoice_partner = False
            return

        xml_decoded = base64.b64decode(self.xml_supplier_approval)
        try:
            factura = etree.fromstring(xml_decoded)
        except Exception as e:
            _logger.info("E-INV CR - This XML file is not XML-compliant. Exception {}".format(e))
            return {"status": 400, "text": _("Excepción de conversión de XML")}

        pretty_xml_string = etree.tostring(
            factura, pretty_print=True, encoding="UTF-8", xml_declaration=True
        )
        _logger.error("E-INV CR - send_file XML: {}".format(pretty_xml_string))
        namespaces = factura.nsmap
        inv_xmlns = namespaces.pop(None)
        namespaces["inv"] = inv_xmlns

        error_message = ""
        if not factura.xpath("inv:Clave", namespaces=namespaces):
            error_message = _(
                "The xml file does not contain the Key node. Please upload a file with the correct format."
            )

        if not factura.xpath("inv:FechaEmision", namespaces=namespaces):
            error_message = _(
                "The xml file does not contain the EmissionDate node. Please upload a file with the correct format."
            )

        if not factura.xpath("inv:Emisor/inv:Identificacion/inv:Numero", namespaces=namespaces):
            error_message = _(
                "The xml file does not contain the Sender node. Please upload a file with the correct format."
            )

        if not factura.xpath("inv:Receptor/inv:Identificacion/inv:Numero", namespaces=namespaces):
            error_message = _(
                "The xml file does not contain the Receiver node. Please upload a file with the correct format."
            )

        if not factura.xpath("inv:ResumenFactura/inv:TotalComprobante", namespaces=namespaces):
            error_message = _(
                "Unable to locate ProofTotal node. Please upload a file with the correct format."
            )
        if error_message:
            return {
                "value": {"xml_supplier_approval": False},
                "warning": {
                    "title": _("Warning"),
                    "message": error_message,
                },
            }

    def load_xml_data(self):
        pass

    def send_mrs_to_hacienda(self):
       pass

    def set_electronic_invoice_data(self):
        detalle_mensaje, tipo, tipo_documento, sequence = self._get_document_type()
        response_json = api_facturae.get_clave_hacienda(
            invoice=self,
            tipo_documento=tipo_documento,
            consecutivo=sequence,
            sucursal_id=self.company_id.sucursal_MR,
            terminal_id=self.company_id.terminal_MR,
        )
        self.consecutive_number_receiver = response_json.get("consecutivo")
        xml = api_facturae.gen_xml_mr_43(
            clave=self.number_electronic,
            cedula_emisor=self.partner_id.vat,
            fecha_emision=self.date_issuance,
            id_mensaje=tipo,
            detalle_mensaje=detalle_mensaje,
            cedula_receptor=self.company_id.vat,
            consecutivo_receptor=self.consecutive_number_receiver,
            monto_impuesto=self.amount_tax_electronic_invoice,
            total_factura=self.amount_total_electronic_invoice,
            codigo_actividad=self.activity_id.code,
            condicion_impuesto="01",
        )
        self.fname_xml_comprobante = "{}_{}.xml".format(tipo_documento, self.number_electronic)
        self.tipo_documento = tipo_documento
        xml_firmado = api_facturae.sign_xml(self.company_id.signature, self.company_id.frm_pin, xml)
        self.xml_comprobante = base64.encodebytes(xml_firmado)
        return (detalle_mensaje, tipo, tipo_documento, sequence)

    def process(self, message_description, detalle_mensaje):
        env = self.company_id.frm_ws_ambiente
        token_m_h = api_facturae.get_token_hacienda(
            inv=self,
            tipo_ambiente=self.company_id.frm_ws_ambiente,
        )
        response_json = api_facturae.send_message(
            inv=self,
            date_cr=api_facturae.get_time_hacienda(),
            xml= self.xml_supplier_approval if self.type in ('in_invoice','in_refund') else self.xml_comprobante,
            token=token_m_h,
            env=env,
        )
        status = response_json.get("status")
        if 200 <= status <= 299:
            self.state_send_invoice = "procesando"
            if self.type in ('out_invoice','out_refun'):
                self.retry(token_m_h, message_description, detalle_mensaje)
        else:
            self.state_send_invoice = "error"
            _logger.error(
                "E-INV CR - Invoice: {}  Error sending Acceptance Message: {}".format(
                    self.number_electronic, response_json.get("text")
                )
            )

    def _get_document_type(self):
        if self.state_invoice_partner == "1":
            detalle_mensaje = _("Accepted")
            tipo = 1
            tipo_documento = "CCE"
            sequence = self.company_id.CCE_sequence_id.next_by_id()
        elif self.state_invoice_partner == "2":
            detalle_mensaje = _("Partial accepted")
            tipo = 2
            tipo_documento = "CPCE"
            sequence = self.company_id.CPCE_sequence_id.next_by_id()
        else:
            detalle_mensaje = _("Rejected")
            tipo = 3
            tipo_documento = "RCE"
            sequence = self.company_id.RCE_sequence_id.next_by_id()
        return (detalle_mensaje, tipo, tipo_documento, sequence)

    def _has_error(self):
        if self.state_send_invoice in ("Accepted", "Rejected", "na"):
            raise UserError(_("Notice!. \n The supplier invoice has already been confirmed"))
        error_message = None
        if abs(self.amount_total_electronic_invoice - self.amount_total) > 1:
            error_message = _("Notice!.\n Total amount does not match the XML amount")
        if not self.xml_supplier_approval:
            error_message = _("Notice!.\n XML file not loaded")
        if not self.company_id.sucursal_MR or not self.company_id.terminal_MR:
            error_message = _(
                "Notice!.\n Please configure the shopping journal, terminal and branch"
            )
        if not self.state_invoice_partner:
            error_message = _(
                "Notice!.\n You must first select the response type for the uploaded file."
            )

        if error_message:
            self.state_send_invoice = "error"
            self.message_post(subject=_("Error"), body=error_message)
        return error_message

    def retry(self, token_m_h, message_description, detalle_mensaje):
        if self.state_send_invoice != "procesando":
            return
        response_json = api_facturae.consulta_clave(
            clave="{}-{}".format(
                self.number_electronic,
                self.consecutive_number_receiver,
            ),
            token=token_m_h,
            tipo_ambiente=self.company_id.frm_ws_ambiente,
        )
        status = response_json["status"]
        if status == 200:
            self.state_send_invoice = response_json.get("ind-estado")
            self.xml_respuesta_tributacion = response_json.get("respuesta-xml")
            self.fname_xml_respuesta_tributacion = "ACH_{}-{}.xml".format(
                self.number_electronic,
                self.consecutive_number_receiver,
            )
            _logger.error("E-INV CR - Estado Documento:{}".format(self.state_send_invoice))
            message_description += (
                "<p><b>You have sent Receiver Message</b>"
                "<br /><b>Document:</b> {}"
                "<br /><b>Consecutive message:</b> {}"
                "<br/><b>Indicated message:</b> {}"
                "</p>".format(
                    self.number_electronic,
                    self.consecutive_number_receiver,
                    detalle_mensaje,
                )
            )
            self.message_post(
                body=message_description, subtype="mail.mt_note", content_subtype="html"
            )
            _logger.info("E-INV CR - Document Status:{}".format(self.state_send_invoice))
        elif status == 400:
            self.state_send_invoice = "ne"
            _logger.error(
                "MAB - Document Acceptance: {}-{} not found in ISR.".format(
                    self.number_electronic, self.consecutive_number_receiver
                )
            )
        else:
            _logger.error("MAB - Unexpected error in Send Acceptance File - Aborting")

    @api.returns("self")
    def refund(
        self,
        date_invoice=None,
        date=None,
        description=None,
        journal_id=None,
        invoice_id=None,
        reference_code_id=None,
    ):
        if self.env.user.company_id.frm_ws_ambiente == "disabled":
            new_invoices = super(AccountInvoice, self).refund()
            return new_invoices
        else:
            new_invoices = self.browse()
            for invoice in self:
                values = self._prepare_refund(
                    invoice,
                    date_invoice=date_invoice,
                    date=date,
                    description=description,
                    journal_id=journal_id,
                )
                values.update({"invoice_id": invoice_id, "reference_code_id": reference_code_id})
                refund_invoice = self.create(values)
                invoice_type = {
                    "out_invoice": ("customer invoices refund"),
                    "in_invoice": ("vendor bill refund"),
                    "out_refund": ("customer refund refund"),
                    "in_refund": ("vendor refund refund"),
                }
                message = _(
                    "This {} has been created from: <a href=# data-oe-model=account.invoice data-oe-id=%d>{}</a>"
                ).format(invoice_type[invoice.type], invoice.id, invoice.number)
                refund_invoice.message_post(body=message)
                refund_invoice.payment_methods_id = invoice.payment_methods_id
                new_invoices += refund_invoice
            return new_invoices

    @api.onchange("partner_id", "company_id")
    def _onchange_partner_id(self):
        super(AccountInvoice, self)._onchange_partner_id()
        self.payment_methods_id = self.partner_id.payment_methods_id

        if self.partner_id and self.partner_id.identification_id and self.partner_id.vat:
            if self.partner_id.country_id.code == "CR":
                self.tipo_documento = "FE"
            else:
                self.tipo_documento = "FEE"
        else:
            self.tipo_documento = "TE"

    @api.model
    def _check_hacienda_for_invoices(self, max_invoices=10):
       return True

    def action_check_hacienda(self):
       pass

    @api.model
    def _check_hacienda_for_mrs(self, max_invoices=10):
        pass

    def action_create_fec(self):
        self.generate_and_send_invoices()

    @api.model
    def _send_invoices_to_hacienda(self, max_invoices=10):
        pass

    def generate_and_send_invoices(self):
       pass

    def validations(self):
        if self.state_invoice_partner==False and self.type in ('in_invoice','in_refund'):
            raise UserError(_("Estimado usuario, debe seleccionar si ACEPTA, ACEPTA PARCIALMENTE O RECHAZA este comprobante."))
    def action_invoice_open(self):
        super(AccountInvoice, self).action_invoice_open()

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        super(AccountInvoice, self)._onchange_partner_id()
        if len(self.partner_id.payment_methods_id) > 0:
            self.payment_methods_id = self.partner_id.payment_methods_id
