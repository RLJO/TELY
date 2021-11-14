import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AccountJournalInherit(models.Model):
    _name = "account.journal"
    _inherit = "account.journal"

    sucursal = fields.Integer(
        string="Sucursal",
        required=False,
        default="1",
    )
    terminal = fields.Integer(
        string="Terminal",
        required=False,
        default="1",
    )
    FE_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Electronic Invoice Sequence",
        required=False,
    )
    TE_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Electronic Ticket Sequence",
        required=False,
    )
    FEE_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Sequence of Electronic Export Invoices",
        required=False,
    )
    NC_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Sequence of Electronic Credit Notes",
        required=False,
    )
    ND_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Electronic Debit Notes Sequence",
        required=False,
    )
    to_process = fields.Boolean(
        default=True,
        help="If is checked, the documents related to this journal will be sended to the API (staging or production, based on company configuration)",
    )

    @api.model
    def set_sequences(self):
        for record in self.search([]):
            record.FE_sequence_id = self.env["ir.sequence"].search(
                [("code", "=", "sequece.FE")], limit=1
            )[0]
            record.TE_sequence_id = self.env["ir.sequence"].search(
                [("code", "=", "sequece.TE")], limit=1
            )[0]
            record.FEE_sequence_id = self.env["ir.sequence"].search(
                [("code", "=", "sequece.FEE")], limit=1
            )[0]
            record.NC_sequence_id = self.env["ir.sequence"].search(
                [("code", "=", "sequece.NC")], limit=1
            )[0]
            record.ND_sequence_id = self.env["ir.sequence"].search(
                [("code", "=", "sequece.ND")], limit=1
            )[0]
