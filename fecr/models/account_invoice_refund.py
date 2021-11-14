import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class AccountInvoiceRefund(models.TransientModel):
    _inherit = "account.invoice.refund"

    @api.model
    def _get_invoice_id(self):
        context = dict(self._context or {})
        return context.get("active_id", "")

    reference_code_id = fields.Many2one(
        comodel_name="reference.code",
        required=True,
    )
    invoice_id = fields.Many2one(
        comodel_name="account.invoice",
        string="Reference",
        default=_get_invoice_id,
        required=False,
    )

    def compute_refund(self, mode="refund"):
        if self.env.user.company_id.frm_ws_ambiente == "disabled":
            result = super(AccountInvoiceRefund, self).compute_refund()
            return result
        else:
            inv_obj = self.env["account.invoice"]
            inv_tax_obj = self.env["account.invoice.tax"]
            inv_line_obj = self.env["account.invoice.line"]
            context = dict(self._context or {})
            xml_id = False

            for form in self:
                created_inv = []
                for inv in inv_obj.browse(context.get("active_ids")):
                    if inv.state in ["draft", "proforma2", "cancel"]:
                        raise UserError(_("Cannot refund draft/proforma/cancelled invoice."))
                    if inv.reconciled and mode in ("cancel", "modify"):
                        raise UserError(
                            _(
                                "Cannot refund invoice which is already reconciled, invoice should be unreconciled first. You can only refund this invoice."
                            )
                        )

                    date = form.date or False
                    description = form.description or inv.name
                    refund = inv.refund(
                        form.date_invoice,
                        date,
                        description,
                        inv.journal_id.id,
                        form.invoice_id.id,
                        form.reference_code_id.id,
                    )

                    created_inv.append(refund.id)

                    if mode in ("cancel", "modify"):
                        movelines = inv.move_id.line_ids
                        to_reconcile_ids = {}
                        to_reconcile_lines = self.env["account.move.line"]
                        for line in movelines:
                            if line.account_id.id == inv.account_id.id:
                                to_reconcile_lines += line
                                to_reconcile_ids.setdefault(line.account_id.id, []).append(line.id)
                            if line.reconciled:
                                line.remove_move_reconcile()

                        refund.payment_term_id = inv.payment_term_id
                        refund.action_invoice_open()
                        for tmpline in refund.move_id.line_ids:
                            if tmpline.account_id.id == inv.account_id.id:
                                to_reconcile_lines += tmpline
                        to_reconcile_lines.filtered(lambda l: l.reconciled is False).reconcile()
                        if mode == "modify":
                            invoice = inv.read(inv_obj._get_refund_modify_read_fields())
                            invoice = invoice[0]
                            del invoice["id"]
                            invoice_lines = inv_line_obj.browse(invoice["invoice_line_ids"])
                            invoice_lines = inv_obj.with_context(
                                mode="modify"
                            )._refund_cleanup_lines(invoice_lines)
                            tax_lines = inv_tax_obj.browse(invoice["tax_line_ids"])
                            tax_lines = inv_obj._refund_cleanup_lines(tax_lines)
                            invoice.update(
                                {
                                    "type": inv.type,
                                    "date_invoice": form.date_invoice,
                                    "state": "draft",
                                    "number": False,
                                    "invoice_line_ids": invoice_lines,
                                    "tax_line_ids": tax_lines,
                                    "date": date,
                                    "origin": inv.origin,
                                    "fiscal_position_id": inv.fiscal_position_id.id,
                                    "invoice_id": inv.id,
                                    "reference_code_id": form.reference_code_id.id,
                                }
                            )
                            for field in inv_obj._get_refund_common_fields():
                                if inv_obj._fields[field].type == "many2one":
                                    invoice[field] = invoice[field] and invoice[field][0]
                                else:
                                    invoice[field] = invoice[field] or False
                            inv_refund = inv_obj.create(invoice)
                            if inv_refund.payment_term_id.id:
                                inv_refund._onchange_payment_term_date_invoice()
                            created_inv.append(inv_refund.id)

                    xml_id = inv.type == 'out_invoice' and 'action_invoice_out_refund' or \
                             inv.type == 'out_refund' and 'action_invoice_tree1' or \
                             inv.type == 'in_invoice' and 'action_invoice_in_refund' or \
                             inv.type == 'in_refund' and 'action_invoice_tree2'
            if xml_id:
                result = self.env.ref('account.%s' % (xml_id)).read()[0]
                if mode == 'modify':
                    # When refund method is `modify` then it will directly open the new draft bill/invoice in form view
                    if inv_refund.type == 'in_invoice':
                        view_ref = self.env.ref('account.invoice_supplier_form')
                    else:
                        view_ref = self.env.ref('account.invoice_form')
                    form_view = [(view_ref.id, 'form')]
                    if 'views' in result:
                        result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
                    else:
                        result['views'] = form_view
                    result['res_id'] = inv_refund.id
                else:
                    invoice_domain = safe_eval(result['domain'])
                    invoice_domain.append(('id', 'in', created_inv))
                    result['domain'] = invoice_domain
                return result
            return True
