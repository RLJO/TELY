import logging

import phonenumbers

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

_TIPOS_CONFIRMACION = (
    # Provides listing of types of comprobante confirmations TODO no se que formato se les puede dejar a este tipo de cosas
    (
        "CCE_sequence_id",
        "account.invoice.supplier.accept.",
        "Supplier invoice acceptance sequence",
    ),
    (
        "CPCE_sequence_id",
        "account.invoice.supplier.partial.",
        "Supplier invoice partial acceptance sequence",
    ),
    (
        "RCE_sequence_id",
        "account.invoice.supplier.reject.",
        "Supplier invoice rejection sequence",
    ),
    (
        "FEC_sequence_id",
        "account.invoice.supplier.reject.",
        "Supplier electronic purchase invoice sequence",
    ),
)


class Company(models.Model):
    _name = "res.company"
    _inherit = [
        "res.company",
        "mail.thread",
    ]

    version_hacienda = fields.Char()
    commercial_name = fields.Char(
        required=False,
    )
    activity_id = fields.Many2many(
        comodel_name="economic_activity",
        string="Economic activity",
        required=True,
    )
    pos_activity_id = fields.Many2one(
        comodel_name="economic_activity",
        string="Economic activity POS",
    )
    signature = fields.Binary(
        string="Cryptographic Key",
    )
    identification_id = fields.Many2one(
        comodel_name="identification.type",
        string="ID Type",
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
    frm_ws_identificador = fields.Char(
        string="Electronic Invoice User",
        required=False,
    )
    frm_ws_password = fields.Char(
        string="Electronic Invoice Password",
        required=False,
    )
    state_name = fields.Char(
        related="state_id.name",
    )
    country_name = fields.Char(
        related="country_id.name",
    )
    district_name = fields.Char(
        related="district_id.name",
    )
    frm_ws_ambiente = fields.Selection(
        selection=[
            ("disabled", _("Disabled")),
            ("api-stag", _("Tests")),
            ("api-prod", _("Production")),
        ],
        string="Environment",
        required=True,
        default="disabled",
        help="It is the environment in which the certificate is being updated. For the quality environment (stag), for the production environment (prod). Required.",
    )
    frm_pin = fields.Char(
        string="Pin",
        required=False,
        help="It is the pin corresponding to the certificate. Required",
    )
    sucursal_MR = fields.Integer(
        string="Subsidairy for MR sequences",
        required=False,
        default="1",
    )
    terminal_MR = fields.Integer(
        string="Terminal for MR sequences",
        required=False,
        default="1",
    )
    CCE_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Sequence Acceptance",
        help="Confirmation sequence of acceptance of electronic receipt. Leave blank and the system will automatically create it for you.",
        readonly=False,
        copy=False,
    )
    CPCE_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Partial Sequence",
        help="Confirmation sequence of partial acceptance of electronic voucher. Leave blank and the system will automatically create it for you.",
        readonly=False,
        copy=False,
    )
    RCE_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Reject Sequence",
        help="Sequence of confirmation of rejection of electronic voucher. Leave blank and the system will automatically create it for you.",
        readonly=False,
        copy=False,
    )
    FEC_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Sequence of Electronic Purchase Invoices",
        readonly=False,
        copy=False,
    )
    html_bank_account1 = fields.Html(
        string="HTML CRC Account",
    )
    html_bank_account2 = fields.Html(
        string="HTML Account USD",
    )

    # leyenda_bill_active = fields.Boolean('Activar leyenda')
    # leyenda_bill_text = fields.Text()

    @api.model
    def create(self, vals):
        """Try to automatically add the Comprobante Confirmation sequence to the company.
        It will attempt to create and assign before storing. The sequence that is
        created will be coded with the following syntax:
            account.invoice.supplier.<tipo>.<company_name>
        where tipo is: accept, partial or reject, and company_name is either the first word
        of the name or commercial name.
        """
        new_comp_id = super(Company, self).create(vals)
        new_comp = self.browse(new_comp_id)
        # new_comp.try_create_configuration_sequences()
        return new_comp.id

    def try_create_confirmation_sequeces(self):
        """Try to automatically add the Comprobante Confirmation sequence to the company.
        It will first check if sequence already exists before attempt to create. The s
        equence is coded with the following syntax:
            account.invoice.supplier.<tipo>.<company_name>
        where tipo is: accept, partial or reject, and company_name is either the first word
        of the name or commercial name.
        """
        company_subname = self.commercial_name
        if not company_subname:
            company_subname = self.name
        company_subname = company_subname.split(" ")[0].lower()
        ir_sequence = self.env["ir.sequence"]
        to_write = {}
        for field, seq_code, seq_name in _TIPOS_CONFIRMACION:
            if not getattr(self, field, None):
                seq_code += company_subname
                seq = self.env.ref(seq_code, raise_if_not_found=False) or ir_sequence.create(
                    {
                        "name": seq_name,
                        "code": seq_code,
                        "implementation": "standard",
                        "padding": 10,
                        "use_date_range": False,
                        "company_id": self.id,
                    }
                )
                to_write[field] = seq.id

        if to_write:
            self.write(to_write)

    @api.onchange("phone")
    def _onchange_phone(self):
        if self.phone:
            phone = phonenumbers.parse(self.phone, self.country_id.code)
            valid = phonenumbers.is_valid_number(phone)
            if not valid:
                alert = {
                    "title": "Atención",
                    "message": _("Invalid phone number"),
                }
                return {"value": {"phone": ""}, "warning": alert}
