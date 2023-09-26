# -*- coding: utf-8 -*-
from odoo import api, fields, models

class CreditCommunication(models.Model):
    """Shell class used to provide a base model to email template and reporting
    Il use this approche in version 7 a browse record
    will exist even if not saved

    """
    _inherit = "credit.control.communication"

    @api.model
    @api.returns('credit.control.line')
    def _get_credit_lines(self, line_ids, partner_id, level_id, currency_id, operating_unit_id=None):
        """ Return credit lines related to a partner and a policy level and operating unit """
        cr_line_obj = self.env['credit.control.line']
        cr_lines = super(CreditCommunication, self)._get_credit_lines(line_ids, partner_id, level_id, currency_id)
        if operating_unit_id:
            domain =[('id', 'in', cr_lines.ids),('invoice_id.operating_unit_id', '=', operating_unit_id)]
            cr_lines = cr_line_obj.search(domain)
        return cr_lines

    @api.model
    def _generate_comm_from_credit_lines(self, lines):
        """ Aggregate credit control line by partner, level, and currency
        It also generate a communication object per aggregation.
        """
        comms = self.browse()
        if not lines:
            return comms
        sql = (
            "SELECT distinct credit_control_line.partner_id, credit_control_line.policy_level_id, "
            " credit_control_line.currency_id, "
            " credit_control_policy_level.level,"
            " account_invoice.operating_unit_id"
            " FROM credit_control_line JOIN credit_control_policy_level "
            "   ON (credit_control_line.policy_level_id = "
            "       credit_control_policy_level.id)"
            "JOIN account_invoice ON (credit_control_line.invoice_id = account_invoice.id)"
            "WHERE credit_control_line.id in %s"
            " ORDER by credit_control_policy_level.level, "
            "          credit_control_line.currency_id"
        )
        cr = self.env.cr
        cr.execute(sql, (tuple(lines.ids),))
        res = cr.dictfetchall()
        company_currency = self.env.user.company_id.currency_id
        for group in res:
            data = {}
            level_lines = self._get_credit_lines(lines.ids,
                                                 group['partner_id'],
                                                 group['policy_level_id'],
                                                 group['currency_id'],
                                                 group['operating_unit_id']
                                                 )
            data['credit_control_line_ids'] = [(6, 0, level_lines.ids)]
            data['partner_id'] = group['partner_id']
            data['current_policy_level'] = group['policy_level_id']
            data['currency_id'] = group['currency_id'] or company_currency.id
            comm = self.create(data)
            comms += comm
        return comms

    
    def post_email_message(self, email, comm):
        """
            Create thread for each partner's mail
        """
        partners = comm.credit_control_line_ids.mapped('partner_id')
        invoices = [inv.number for inv in comm.credit_control_line_ids.mapped('invoice_id')]
        from datetime import datetime
        msg = "Abundant has been sent on " + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) +"\n"+email.body if email.body else ''
        mail_values = {
            'subject': email.subject,
            'body': msg,
            # 'partner_ids':[partner.id for partner in partners],
            'attachment_ids': [attach.id for attach in email.attachment_ids],
            'author_id': email.author_id.id,
            'email_from': email.email_from,
            'record_name': ','.join(invoices) if invoices else email.record_name,
            'no_auto_thread': email.no_auto_thread,
            'mail_server_id': email.mail_server_id.id,
            'reply_to': email.reply_to,
        }
        subtype_id = self.sudo().env.ref('mail.mt_comment', raise_if_not_found=False).id
        return partners.message_post(message_type='comment',subtype_id=subtype_id, **mail_values)

    
    @api.returns('mail.mail')
    def _generate_emails(self):
        """
            Inherit to add thread to each partner
        """
        emails = super(CreditCommunication, self)._generate_emails()
        for comm in self:
            email = comm.credit_control_line_ids.mapped('mail_message_id')
            self.post_email_message(email, comm)
        return emails