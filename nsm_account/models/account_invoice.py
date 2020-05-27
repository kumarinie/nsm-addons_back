# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2015 Magnus
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

from odoo import api, fields, models, _


class Invoice(models.Model):
    _inherit = "account.invoice"

    name = fields.Char(string='Reference/Description', index=True,
        readonly=True, states={'draft': [('readonly', False)],'open':[('readonly',False)]},
        copy=False, help='The name that will be used on account move lines')

    klantnummer = fields.Char(related='partner_id.aprofit_nummer', readonly=True, relation='res.partner',
                              store=False, string='aProfit Klantnummer')
    invoice_description = fields.Text('Description')


    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent
        """
        self.ensure_one()
        self.sent = True
        return self.env['report'].get_action(self, 'nsm_account.report_invoice_nsm_account')

    @api.multi
    def button_merge_attachments(self):
        '''
            Prints the merged Reports
        '''

        mergePDF = self.env['supplier.invoice.merge.pdf']
        vals = mergePDF.default_get(['file_name', 'file_data'])
        res = mergePDF.create(vals)
        # return self.env['report'].get_action(self, 'account.invoice.customNSM')

        view = self.env.ref('nsm_account.view_suplier_invoice_merge_pdf_form')
        return {
            'name': _('Merge PDF'),
            'context': self._context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'supplier.invoice.merge.pdf',
            'res_id': res.id,
            'views': [(view.id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

