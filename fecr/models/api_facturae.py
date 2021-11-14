import base64
import datetime
import json
import logging
import os
import random
import re
import time
from io import BytesIO
from xml.sax.saxutils import escape

import phonenumbers
import pytz
import requests
from lxml import etree
from phonenumbers import NumberParseException

from odoo import _
from odoo.exceptions import UserError

from ..xades.context2 import PolicyId2, XAdESContext2, create_xades_epes_signature
from . import fe_enums

try:
    from OpenSSL import crypto
except (ImportError, IOError) as err:
    logging.info(err)

_logger = logging.getLogger(__name__)


class RequestError(Exception):
    """Request Exception"""


def sign_xml(
    cert,
    password,
    xml,
    policy_id="https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/"
    "2016/v4.2/ResolucionComprobantesElectronicosDGT-R-48-2016_4.2.pdf",
):
    root = etree.fromstring(xml)
    signature = create_xades_epes_signature()
    policy = PolicyId2()
    policy.id = policy_id
    root.append(signature)
    ctx = XAdESContext2(policy)
    certificate = crypto.load_pkcs12(base64.b64decode(cert), password)
    ctx.load_pkcs12(certificate)
    ctx.sign(signature)

    return etree.tostring(
        root, encoding="UTF-8", method="xml", xml_declaration=True, with_tail=False
    )


def get_time_hacienda():
    now_utc = datetime.datetime.now(pytz.timezone("UTC"))
    now_cr = now_utc.astimezone(pytz.timezone("America/Costa_Rica"))
    date_cr = now_cr.strftime("%Y-%m-%dT%H:%M:%S-06:00")

    return date_cr


def limit(string, limit):
    return (string[: limit - 3] + "...") if len(string) > limit else string


def get_mr_sequencevalue(inv):
    mr_mensaje_id = int(inv.state_invoice_partner)
    if mr_mensaje_id < 1 or mr_mensaje_id > 3:
        raise UserError(_("The receiving message ID is invalid."))
    elif mr_mensaje_id is None:
        raise UserError(_("A valid ID has not been provided for the MR."))

    if inv.state_invoice_partner == "1":
        detalle_mensaje = "Aceptado"
        tipo = 1
        tipo_documento = fe_enums.TipoDocumento["CCE"]
        sequence = inv.env["ir.sequence"].next_by_code("sequece.electronic.doc.confirmation")

    elif inv.state_invoice_partner == "2":
        detalle_mensaje = "Aceptado parcial"
        tipo = 2
        tipo_documento = fe_enums.TipoDocumento["CPCE"]
        sequence = inv.env["ir.sequence"].next_by_code(
            "sequece.electronic.doc.partial.confirmation"
        )
    else:
        detalle_mensaje = "Rechazado"
        tipo = 3
        tipo_documento = fe_enums.TipoDocumento["RCE"]
        sequence = inv.env["ir.sequence"].next_by_code("sequece.electronic.doc.reject")

    return {
        "detalle_mensaje": detalle_mensaje,
        "tipo": tipo,
        "tipo_documento": tipo_documento,
        "sequence": sequence,
    }


def get_consecutivo_hacienda(tipo_documento, consecutivo, sucursal_id, terminal_id):
    tipo_doc = fe_enums.TipoDocumento[tipo_documento]
    inv_consecutivo = str(consecutivo).zfill(10)
    inv_sucursal = str(sucursal_id).zfill(3)
    inv_terminal = str(terminal_id).zfill(5)
    consecutivo_mh = inv_sucursal + inv_terminal + tipo_doc + inv_consecutivo

    return consecutivo_mh


def get_clave_hacienda(
    invoice, tipo_documento, consecutivo, sucursal_id, terminal_id, situacion="normal"
):
    tipo_doc = fe_enums.TipoDocumento[tipo_documento]
    inv_consecutivo = re.sub("[^0-9]", "", consecutivo)
    if len(inv_consecutivo) != 10:
        raise UserError(_("The numbering must have 10 digits"))

    inv_sucursal = re.sub("[^0-9]", "", str(sucursal_id)).zfill(3)
    inv_terminal = re.sub("[^0-9]", "", str(terminal_id)).zfill(5)

    consecutivo_mh = inv_sucursal + inv_terminal + tipo_doc + inv_consecutivo

    if not invoice.company_id.identification_id:
        raise UserError(_("Select the type of issuer identification in the company profile"))

    inv_cedula = re.sub("[^0-9]", "", invoice.company_id.vat)

    if invoice.company_id.identification_id.code == "01" and len(inv_cedula) != 9:
        raise UserError(_("The issuer's Physical ID must have 9 digits"))
    elif invoice.company_id.identification_id.code == "02" and len(inv_cedula) != 10:
        raise UserError(_("The Issuer's Legal Certificate must have 10 digits"))
    elif invoice.company_id.identification_id.code == "03" and (
        len(inv_cedula) != 11 or len(inv_cedula) != 12
    ):
        raise UserError(_("The issuer's DIMEX identification must have 11 or 12 digits"))
    elif invoice.company_id.identification_id.code == "04" and len(inv_cedula) != 10:
        raise UserError(_("The issuer's NITE ID must have 10 digits"))

    inv_cedula = str(inv_cedula).zfill(12)

    cedula_emisor = limit(inv_cedula, 20)

    situacion_comprobante = fe_enums.SituacionComprobante.get(situacion)
    if not situacion_comprobante:
        raise UserError(
            _("The situation indicated for the electronic receipt is invalid: ") + situacion
        )

    now_utc = datetime.datetime.now(pytz.timezone("UTC"))
    now_cr = now_utc.astimezone(pytz.timezone("America/Costa_Rica"))
    cur_date = now_cr.strftime("%d%m%y")

    try:
        phone = phonenumbers.parse(
            invoice.company_id.phone,
            invoice.company_id.country_id and invoice.company_id.country_id.code or "CR",
        )
    except NumberParseException:
        raise UserError(
            _(
                "In data included in the company's phone number {} does not appear to be a phone number, Please verify."
            ).format(invoice.company_id.name)
        )

    codigo_pais = str(phone and phone.country_code or 506)
    codigo_seguridad = str(random.randint(1, 99999999)).zfill(8)
    clave_hacienda = (
        codigo_pais
        + cur_date
        + cedula_emisor
        + consecutivo_mh
        + situacion_comprobante
        + codigo_seguridad
    )

    return {
        "length": len(clave_hacienda),
        "clave": clave_hacienda,
        "consecutivo": consecutivo_mh,
    }


last_tokens = {}
last_tokens_time = {}
last_tokens_expire = {}
last_tokens_refresh = {}


def get_token_hacienda(inv, tipo_ambiente):
    global last_tokens
    global last_tokens_time
    global last_tokens_expire
    global last_tokens_refresh

    token = last_tokens.get(inv.company_id.id, False)
    token_time = last_tokens_time.get(inv.company_id.id, False)
    token_expire = last_tokens_expire.get(inv.company_id.id, 0)
    current_time = time.time()

    if token and (current_time - token_time < token_expire - 10):
        token_hacienda = token
    else:
        headers = {}
        data = {
            "client_id": tipo_ambiente,
            "client_secret": "",
            "grant_type": "password",
            "username": inv.company_id.frm_ws_identificador,
            "password": inv.company_id.frm_ws_password,
        }

        endpoint = fe_enums.UrlHaciendaToken[tipo_ambiente]

        try:
            response = requests.request("POST", endpoint, data=data, headers=headers)
            response_json = response.json()
            if 200 <= response.status_code <= 299:
                token_hacienda = response_json.get("access_token")
                last_tokens[inv.company_id.id] = token
                last_tokens_time[inv.company_id.id] = time.time()
                last_tokens_expire[inv.company_id.id] = response_json.get("expires_in")
                last_tokens_refresh[inv.company_id.id] = response_json.get("refresh_expires_in")
            else:
                _logger.error(
                    "MAB - token_hacienda failed. error: {} \n {}".format(
                        response.status_code, response.reason
                    )
                )
                raise Exception(
                    "MAB - token_hacienda failed. error: {} \n {}".format(
                        response.status_code, response.reason
                    )
                )

        except requests.exceptions.RequestException as e:
            raise Warning(_("Error Obtaining the Token from MH. Exception {}".format(e)))

    return token_hacienda


def refresh_token_hacienda(tipo_ambiente, token):
    headers = {}
    data = {
        "client_id": tipo_ambiente,
        "client_secret": "",
        "grant_type": "refresh_token",
        "refresh_token": token,
    }

    endpoint = fe_enums.UrlHaciendaToken[tipo_ambiente]

    try:
        response = requests.request("POST", endpoint, data=data, headers=headers)
        response_json = response.json()
        token_hacienda = response_json.get("access_token")
        return token_hacienda
    except ImportError:
        raise Warning(_("Error Refreshing the Token from MH"))


def gen_xml_mr_43(
    clave,
    cedula_emisor,
    fecha_emision,
    id_mensaje,
    detalle_mensaje,
    cedula_receptor,
    consecutivo_receptor,
    monto_impuesto=0,
    total_factura=0,
    codigo_actividad=False,
    condicion_impuesto=False,
    monto_total_impuesto_acreditar=False,
    monto_total_gasto_aplicable=False,
):
    sb = StringBuilder()

    return str(sb)


def gen_xml_fe_v43(
    inv,
    sale_conditions,
    total_servicio_gravado,
    total_servicio_exento,
    totalServExonerado,
    total_mercaderia_gravado,
    total_mercaderia_exento,
    totalMercExonerada,
    totalOtrosCargos,
    base_total,
    total_impuestos,
    total_descuento,
    lines,
    otrosCargos,
    currency_rate,
    invoice_comments,
):
    numero_linea = 0
    if inv._name == "pos.order":
        activity_id = inv.company_id.pos_activity_id
        plazo_credito = "0"
        payment_methods_id = "01"
        cod_moneda = str(inv.company_id.currency_id.name)
    else:
        activity_id = inv.activity_id
        payment_methods_id = str(inv.payment_methods_id.sequence)
        plazo_credito = str(
            inv.payment_term_id
            and inv.payment_term_id.line_ids
            and inv.payment_term_id.line_ids[0].days
            or 0
        )
        cod_moneda = str(inv.currency_id.name)

    sb = StringBuilder()

    return sb


def gen_xml_fee_v43(
    inv,
    sale_conditions,
    total_servicio_gravado,
    total_servicio_exento,
    totalServExonerado,
    total_mercaderia_gravado,
    total_mercaderia_exento,
    totalMercExonerada,
    totalOtrosCargos,
    base_total,
    total_impuestos,
    total_descuento,
    lines,
    otrosCargos,
    currency_rate,
    invoice_comments,
):
    numero_linea = 0
    sb = StringBuilder()
    return sb


def gen_xml_te_43(
    inv,
    sale_conditions,
    total_servicio_gravado,
    total_servicio_exento,
    totalServExonerado,
    total_mercaderia_gravado,
    total_mercaderia_exento,
    totalMercExonerada,
    totalOtrosCargos,
    base_total,
    total_impuestos,
    total_descuento,
    lines,
    currency_rate,
    invoice_comments,
    otrosCargos,
):


    sb = StringBuilder()


    return sb


def gen_xml_nc_v43(
    inv,
    sale_conditions,
    total_servicio_gravado,
    total_servicio_exento,
    totalServExonerado,
    total_mercaderia_gravado,
    total_mercaderia_exento,
    totalMercExonerada,
    totalOtrosCargos,
    base_total,
    total_impuestos,
    total_descuento,
    lines,
    tipo_documento_referencia,
    numero_documento_referencia,
    fecha_emision_referencia,
    codigo_referencia,
    razon_referencia,
    currency_rate,
    invoice_comments,
    otrosCargos,
):
    sb = StringBuilder()
    return sb


def gen_xml_nd_v43(
    inv,
    consecutivo,
    sale_conditions,
    total_servicio_gravado,
    total_servicio_exento,
    total_mercaderia_gravado,
    total_mercaderia_exento,
    base_total,
    total_impuestos,
    total_descuento,
    lines,
    tipo_documento_referencia,
    numero_documento_referencia,
    fecha_emision_referencia,
    codigo_referencia,
    razon_referencia,
    currency_rate,
    invoice_comments,
):
    numero_linea = 0

    sb = StringBuilder()
    return sb


def gen_xml_fec_v43(
    inv,
    sale_conditions,
    total_servicio_gravado,
    total_servicio_exento,
    totalServExonerado,
    total_mercaderia_gravado,
    total_mercaderia_exento,
    totalMercExonerada,
    totalOtrosCargos,
    base_total,
    total_impuestos,
    total_descuento,
    lines,
    otrosCargos,
    currency_rate,
    invoice_comments,
):
    numero_linea = 0
    activity_id = inv.activity_id
    if inv._name == "pos.order":
        activity_id = inv.company_id.pos_activity_id
        plazo_credito = "0"
        payment_methods_id = "01"
        cod_moneda = str(inv.company_id.currency_id.name)
    else:
        payment_methods_id = str(inv.payment_methods_id.sequence)
        plazo_credito = str(inv.payment_term_id and inv.payment_term_id.line_ids[0].days or 0)
        cod_moneda = str(inv.currency_id.name)

    sb = StringBuilder()

    return sb


def send_xml_fe(inv, token, date, xml, tipo_ambiente):
    headers = {"Authorization": "Bearer " + token, "Content-type": "application/json"}
    endpoint = fe_enums.UrlHaciendaRecepcion[tipo_ambiente]
    xml_base64 = stringToBase64(xml)
    data = {
        "clave": inv.number_electronic,
        "fecha": date,
        "emisor": {
            "tipoIdentificacion": inv.company_id.identification_id.code,
            "numeroIdentificacion": inv.company_id.vat,
        },
        "comprobanteXml": xml_base64,
    }
    if inv.partner_id:
        data["receptor"] = {
            "tipoIdentificacion": inv.partner_id.identification_id.code or "",
            "numeroIdentificacion": inv.partner_id.vat or "",
        }

    json_hacienda = json.dumps(data)

    try:
        response = requests.request("POST", endpoint, data=json_hacienda, headers=headers)

        if response.status_code != 202:
            error_caused_by = (
                response.headers.get("X-Error-Cause") if "X-Error-Cause" in response.headers else ""
            )
            error_caused_by += response.headers.get("validation-exception", "")
            _logger.info("Status: {}, Text {}".format(response.status_code, error_caused_by))
            return {"status": response.status_code, "text": error_caused_by}
        else:
            return {"status": response.status_code, "text": response.reason}

    except ImportError:
        raise Warning(_("Error sending the XML to the Ministry of Finance"))


def schema_validator(xml_file, xsd_file):
    xmlschema = etree.XMLSchema(
        etree.parse(os.path.join(os.path.dirname(__file__), "xsd/" + xsd_file))
    )
    xml_doc = base64decode(xml_file)
    root = etree.fromstring(xml_doc, etree.XMLParser(remove_blank_text=True))
    result = xmlschema.validate(root)
    return result


def get_invoice_attachments(invoice, record_id):
    attachments = []
    attachment = invoice.env["ir.attachment"].search(
        [
            ("res_model", "=", "account.invoice"),
            ("res_id", "=", record_id),
            ("res_field", "=", "xml_comprobante"),
        ],
        limit=1,
    )

    if attachment.id:
        attachment.name = invoice.fname_xml_comprobante
        attachment.datas_fname = invoice.fname_xml_comprobante
        attachments.append(attachment.id)

    attachment_resp = invoice.env["ir.attachment"].search(
        [
            ("res_model", "=", "account.invoice"),
            ("res_id", "=", record_id),
            ("res_field", "=", "xml_respuesta_tributacion"),
        ],
        limit=1,
    )

    if attachment_resp.id:
        attachment_resp.name = invoice.fname_xml_respuesta_tributacion
        attachment_resp.datas_fname = invoice.fname_xml_respuesta_tributacion
        attachments.append(attachment_resp.id)
    return attachments


def parse_xml(name):
    return etree.parse(name).getroot()


def stringToBase64(s):
    return base64.b64encode(s).decode()


def stringStrip(s, start, end):
    return s[start:-end]


def base64decode(string_decode):
    return base64.b64decode(string_decode)


def base64UTF8Decoder(s):
    return s.decode("utf-8")


class StringBuilder:
    _file_str = None

    def __init__(self):
        self._file_str = BytesIO()

    def Append(self, text):
        type_text = type(text)
        if type_text == str:
            text = text.encode("ascii", "xmlcharrefreplace")
        self._file_str.write(text)

    def __str__(self):
        return self._file_str.getvalue().decode("utf-8")


def consulta_clave(clave, token, tipo_ambiente):
    endpoint = fe_enums.UrlHaciendaRecepcion[tipo_ambiente] + clave
    headers = {
        "Authorization": "Bearer {}".format(token),
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded",
        "Postman-Token": "bf8dc171-5bb7-fa54-7416-56c5cda9bf5c",
    }

    _logger.debug("MAB - consulta_clave - url: {}".format(endpoint))

    try:
        response = requests.get(endpoint, headers=headers)
    except requests.exceptions.RequestException as e:
        _logger.error("Exception {}".format(e))
        return {"status": -1, "text": "Excepcion {}".format(e)}

    if 200 <= response.status_code <= 299:
        response_json = {
            "status": 200,
            "ind-estado": response.json().get("ind-estado"),
            "respuesta-xml": response.json().get("respuesta-xml"),
        }
    elif 400 <= response.status_code <= 499:
        response_json = {
            "status": 400,
            "ind-estado": "error",
            "cause": response.headers["X-Error-Cause"],
        }
    else:
        _logger.error("MAB - consulta_clave failed.  error: {}".format(response.status_code))
        response_json = {
            "status": response.status_code,
            "text": "token_hacienda failed: {}".format(response.reason),
        }
    return response_json


def consulta_documentos(self, inv, env, token_m_h, date_cr, xml_firmado):

    return estado_m_h == "aceptado"


def send_message(inv, date_cr, xml, token, env):
    endpoint = fe_enums.UrlHaciendaRecepcion[env]
    vat = re.sub("[^0-9]", "", inv.partner_id.vat)
    xml_base64 = stringToBase64(xml)
    comprobante = {
        "clave": inv.number_electronic,
        "consecutivoReceptor": inv.consecutive_number_receiver,
        "fecha": date_cr,
        "emisor": {
            "tipoIdentificacion": str(inv.partner_id.identification_id.code),
            "numeroIdentificacion": vat,
        },
        "receptor": {
            "tipoIdentificacion": str(inv.company_id.identification_id.code),
            "numeroIdentificacion": inv.company_id.vat,
        },
        "comprobanteXml": xml_base64,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(token),
    }
    try:
        response = requests.post(endpoint, data=json.dumps(comprobante), headers=headers)

    except requests.exceptions.RequestException as e:
        _logger.info("Exception {}".format(e))
        return {"status": 400, "text": "Excepción de envio XML"}

    if not (200 <= response.status_code <= 299):
        _logger.error(
            "MAB - ERROR SEND MESSAGE - RESPONSE:{}".format(
                response.headers.get("X-Error-Cause", "Unknown")
            )
        )

        return {
            "status": response.status_code,
            "text": response.headers.get("X-Error-Cause", "Unknown"),
        }
    else:
        return {"status": response.status_code, "text": response.text}
