import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def message_route_process(self, message, message_dict, routes):
        self = self.with_context(attachments_mime_plainxml=True)  # import XML attachments as text
        # postpone setting message_dict.partner_ids after message_post, to avoid double notifications
        original_partner_ids = message_dict.pop("partner_ids", [])
        thread_id = False
        for model, thread_id, custom_values, user_id, _alias in routes or ():
            if model:
                Model = self.env[model]
                if not (
                    thread_id and hasattr(Model, "message_update") or hasattr(Model, "message_new")
                ):
                    raise ValueError(
                        "Undeliverable mail with Message-Id %s, model %s does not accept incoming emails"
                        % (message_dict["message_id"], model)
                    )

                # disabled subscriptions during message_new/update to avoid having the system user running the
                # email gateway become a follower of all inbound messages
                MessageModel = Model.sudo(user_id).with_context(
                    mail_create_nosubscribe=True, mail_create_nolog=True
                )
                if thread_id and hasattr(MessageModel, "message_update"):
                    thread = MessageModel.browse(thread_id)
                    thread.message_update(message_dict)
                else:
                    # if a new thread is created, parent is irrelevant
                    message_dict.pop("parent_id", None)
                    thread = MessageModel.message_new(message_dict, custom_values)
                    thread_id = thread.id
            else:
                if thread_id:
                    raise ValueError(
                        "Posting a message without model should be with a null res_id, to create a private message."
                    )
                thread = self.env["mail.thread"]

            # replies to internal message are considered as notes, but parent message
            # author is added in recipients to ensure he is notified of a private answer
            partner_ids = []
            if message_dict.pop("internal", False):
                subtype = "mail.mt_note"
                if message_dict.get("parent_id"):
                    parent_message = (
                        self.env["mail.message"].sudo().browse(message_dict["parent_id"])
                    )
                    if parent_message.author_id:
                        partner_ids = [(4, parent_message.author_id.id)]
            else:
                subtype = "mail.mt_comment"

            post_params = dict(subtype=subtype, partner_ids=partner_ids, **message_dict)
            if not hasattr(thread, "message_post"):
                post_params["model"] = model

            if model == "account.invoice":
                thread = thread.with_context({"invoice_from_incoming_mail": True})

            new_msg = thread.message_post(**post_params)

            if new_msg and original_partner_ids:
                # postponed after message_post, because this is an external message and we don't want to create
                # duplicate emails due to notifications
                new_msg.write({"partner_ids": original_partner_ids})

            # Add xml attached on email to invoice and call load_xml_data()
            if model == "account.invoice":
                logging.info(thread)
                thread.type = "in_invoice"
                xml_attachment = self.env["ir.attachment"].search(
                    [
                        ("res_id", "=", thread.id),
                        ("res_model", "=", model),
                    ]
                )
                if xml_attachment and xml_attachment.datas_fname[-3:] == "xml":
                    thread.fname_xml_supplier_approval = xml_attachment.datas_fname
                    thread.xml_supplier_approval = xml_attachment.datas
                    # thread.fname_xml_comprobante = xml_attachment.datas_fname
                    # thread.xml_comprobante = xml_attachment.datas
                    thread.load_xml_data()

        return thread_id
