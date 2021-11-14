import logging
import re

import phonenumbers
import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError

NIF_API = "https://api.hacienda.go.cr/fe/ae"

_logger = logging.getLogger(__name__)


class PartnerElectronic(models.Model):
    _inherit = "res.partner"

    commercial_name = fields.Char(
        required=False,
    )
    state_id = fields.Many2one(
        comodel_name="res.country.state",
        required=False,
    )
    district_id = fields.Many2one(
        comodel_name="res.country.district",
        required=False,
    )
    county_id = fields.Many2one(
        comodel_name="res.country.county",
        required=False,
    )
    neighborhood_id = fields.Many2one(
        comodel_name="res.country.neighborhood",
        required=False,
    )
    identification_id = fields.Many2one(
        comodel_name="identification.type",
        string="ID Type",
        required=False,
    )
    payment_methods_id = fields.Many2one(
        comodel_name="payment.methods",
        required=False,
    )
    has_exoneration = fields.Boolean(
        required=False,
    )
    type_exoneration = fields.Many2one(
        comodel_name="aut.ex",
        required=False,
    )
    exoneration_number = fields.Char(
        required=False,
    )
    institution_name = fields.Char(
        string="Issuing Institution",
        required=False,
    )
    date_issue = fields.Date(
        required=False,
    )
    date_expiration = fields.Date(
        required=False,
    )
    _sql_constraints = [
        (
            "vat_unique",
            "CHECK(1=1)",  # For production DB's
            _("No pueden existir dos clientes/proveedores con el mismo número de identificación"),
        )
    ]

    @api.onchange("phone")
    def _onchange_phone(self):
        if self.phone:
            phone = phonenumbers.parse(self.phone, self.country_id and self.country_id.code or "CR")
            valid = phonenumbers.is_valid_number(phone)
            if not valid:
                alert = {
                    "title": "Atención",
                    "message": _("Invalid phone numbe"),
                }
                return {"value": {"phone": ""}, "warning": alert}

    @api.onchange("mobile")
    def _onchange_mobile(self):
        if self.mobile:
            mobile = phonenumbers.parse(
                self.mobile, self.country_id and self.country_id.code or "CR"
            )
            valid = phonenumbers.is_valid_number(mobile)
            if not valid:
                alert = {"title": _("Attention"), "message": _("Invalid phone numbe")}
                return {"value": {"mobile": ""}, "warning": alert}

    @api.onchange("email")
    def _onchange_email(self):
        if self.email:
            if not re.match(
                r"^(\s?[^\s,]+@[^\s,]+\.[^\s,]+\s?,)*(\s?[^\s,]+@[^\s,]+\.[^\s,]+)$",
                self.email.lower(),
            ):
                vals = {"email": False}
                alerta = {
                    "title": _("Attention"),
                    "message": _("The email does not comply with a valid structure.")
                    + str(self.email),
                }
                return {"value": vals, "warning": alerta}

    @api.onchange("vat", "identification_id")
    def _verify_vat_and_identification_id(self):
        if not (self.identification_id and self.vat):
            return
        self.vat = re.sub(r"[^\d]", "", self.vat)
        lens = {
            "01": (9, 9),
            "02": (10, 10),
            "03": (11, 12),
            "04": (9, 9),
            "05": (20, 20),
        }
        limits = lens[self.identification_id.code]
        if not limits[0] <= len(self.vat) <= limits[1]:
            raise UserError(
                _("VAT must be between {} and {} (inclusive) chars long").format(
                    limits[0],
                    limits[1],
                )
            )

    @api.onchange("vat")
    def _get_name_from_vat(self):
        if not self.vat:
            return
        response = requests.get(NIF_API, params={"identificacion": self.vat})
        if response.status_code == 200:
            response_json = response.json()
            self.name = response_json["nombre"]
            self.identification_id = self.identification_id.search(
                [("code", "=", response_json["tipoIdentificacion"])], limit=1
            )
            return
        elif response.status_code == 404:
            title = "VAT Not found"
            message = "The VAT is not on the API"
        elif response.status_code == 400:
            title = "API Error 400"
            message = "Bad Request"
        else:
            title = "Unknown Error"
            message = "Unknown error in the API request"
        return {
            "warning": {
                "title": title,
                "message": message,
            }
        }
