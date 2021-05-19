
from odoo import _, api, fields, models


class Invite(models.TransientModel):
    _inherit = 'mail.wizard.invite'

    @api.multi
    def add_followers(self):
        email_from = self.env['mail.message']._get_default_from()
        for wizard in self:
            Model = self.env[wizard.res_model]
            document = Model.browse(wizard.res_id)

            # filter partner_ids to get the new followers, to avoid sending email to already following partners
            new_partners = wizard.partner_ids - document.message_partner_ids
            new_channels = wizard.channel_ids - document.message_channel_ids
            document.message_subscribe(new_partners.ids, new_channels.ids)

            model_ids = self.env['ir.model'].search([('model', '=', wizard.res_model)])
            model_name = model_ids.name_get()[0][1]
            # send an email if option checked and if a message exists (do not send void emails)
            if wizard.send_mail and wizard.message and not wizard.message == '<br>':  # when deleting the message, cleditor keeps a <br>
                message = self.env['mail.message'].create({
                    'subject': _('Invitation to follow %s: %s') % (model_name, document.name_get()[0][1]),
                    'body': wizard.message,
                    'record_name': document.name_get()[0][1],
                    'email_from': email_from,
                    'reply_to': email_from,
                    'model': wizard.res_model,
                    'res_id': wizard.res_id,
                    'no_auto_thread': True,
                })
                new_partners.filtered(lambda rp: not rp.stop_followers_mail).with_context(auto_delete=True)._notify(message, force_send=True, send_after_commit=False,
                                                                    user_signature=True)
                message.unlink()
        return {'type': 'ir.actions.act_window_close'}
