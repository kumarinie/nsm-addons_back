# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2014 BAS Solutions
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class WizardUser(models.TransientModel):
    _inherit = 'portal.wizard.user'

    operating_unit_ids = fields.Many2many('operating.unit', string='Operating Units')

    
    def _send_email(self):
        """ send notification email to a new portal user """
        if not self.env.user.email:
            raise UserError(_('You must have an email address in your User Preferences to send emails.'))

        grp = "nsm_supplier_portal.group_module_supplier_portal_user"
        template = self.env.ref('portal.mail_template_data_portal_welcome')

        for wizard_line in self:

            if (grp,'in', [x.get_xml_id() for x in wizard_line.user_id.groups_id]):

                lang = wizard_line.user_id.lang
                partner = wizard_line.user_id.partner_id

                portal_url = partner.with_context(signup_force_type_in_url='', lang=lang)._get_signup_url_for_action()[partner.id]
                partner.signup_prepare()

                if template:
                    return template.with_context(dbname=self._cr.dbname, portal_url=portal_url, lang=lang).send_mail(wizard_line.id, force_send=True)
                else:
                    _logger.warning("No email template found for sending email to the portal user")

        return super(WizardUser, self)._send_email()



    
    def action_apply(self):

        for wiz_user in self.sudo(SUPERUSER_ID):
            if wiz_user.in_portal:
                partner = wiz_user.partner_id
                if not partner.product_category_ids:
                    raise UserError(_('For this supplier [%s] to be invited to the Portal you have to grant him one or more Invoice Categories and one or more Titles/Departments.' % partner.name))

                if not partner.analytic_account_ids:
                    if not partner.product_price_ids:
                       raise UserError(_('For this supplier [%s] to be invited to the Portal you have to grant him one or more Invoice Categories and one or more Titles/Departments/Prices.' % partner.name))

        return super(WizardUser, self).action_apply()

    
    def _create_user(self):
        """ update operating unit for the newly created user for wizard_user.partner_id
            :returns record of res.users
        """
        user = super(WizardUser, self)._create_user()
        user.write({'default_operating_unit_id': False,'operating_unit_ids': [(6, 0, self.operating_unit_ids.ids)]})
        return user

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
