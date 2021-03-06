from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    expense_account_id = fields.Many2one(
        comodel_name="account.account",
        company_dependent=True,
        string="Default Expense Account for FE invoice import",
        domain=[("deprecated", "=", False)],
        help="The expense account used when importing Costa Rican electronic invoice automatically",
    )
    load_lines = fields.Boolean(
        string="Indicates if invoice lines should be load when loading a Costa Rican Digital Invoice",
    )
    reimbursable_email = fields.Char(
        string='This email is searched in the "to" of the email to mark the invoice as refundable',
        required=False,
        copy=False,
        index=True,
    )
    notification_email = fields.Char(
        string="Address to which any notification related to FE is sent",
        required=False,
        copy=False,
        index=True,
    )

    apply_terms_conditions = fields.Boolean('Terminos y condiciones en reporte',default=False)

    # Todo Nuevo 08-11-21
    einvoice_fields_add = fields.Boolean(string=u"Agregar datos adiconales en XML", implied_group='account.group_account_manager')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env["ir.config_parameter"].sudo().get_param
        res.update(
            expense_account_id=int(get_param("expense_account_id")),
            load_lines=get_param("load_lines"),
            reimbursable_email=get_param("reimbursable_email"),
            notification_email=get_param("notification_email"),
            apply_terms_conditions=get_param("apply_terms_conditions"),
            einvoice_fields_add=self.env['ir.config_parameter'].get_param('einvoice_fields_add')  # Todo Nuevo 08-11-21

        )
        return res

    # # este set values no anda
    # @api.model
    # def set_values(self):
    #     super(ResConfigSettings, self).set_values()
    #     set_param = self.env["ir.config_parameter"].sudo().set_param
    #     set_param("expense_account_id", self.expense_account_id.id)
    #     set_param("load_lines", self.load_lines)
    #     set_param("reimbursable_email", self.reimbursable_email)
    #     set_param("notification_email", self.notification_email)

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('apply_terms_conditions', self.apply_terms_conditions)
        self.env['sale.order'].sudo().search([]).write({'apply_terms_conditions': self.apply_terms_conditions})
        self.env['ir.config_parameter'].set_param('einvoice_fields_add', self.einvoice_fields_add)  # Todo Nuevo 08-11-21
