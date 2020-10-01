# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Eurogroup Consulting NL (<http://eurogroupconsulting.nl>).
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


from odoo import models, fields, api, _

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    verif_tresh_exceeded_2 = fields.Boolean(string='Verification Treshold 2',
                                          store=True, readonly=True, compute='_compute_amount',
                                          track_visibility='always', copy=False)

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
        if self.type in ('in_invoice', 'in_refund'):
            self.user_id = self.env.user
        return res

    @api.multi
    def write(self, vals):
        res = super(AccountInvoice, self).write(vals)
        for inv in self:
            if 'invoice_line_ids' in vals:
                if inv.type in ('in_invoice', 'in_refund'):
                    invoice_line = inv.invoice_line_ids and inv.invoice_line_ids[0]
                    if invoice_line.account_analytic_id:
                        team_acc_mapp = self.env['sales.team'].search([('analytic_account_id','=',invoice_line.account_analytic_id.id)], limit=1)
                        if team_acc_mapp and team_acc_mapp.sales_team_id:
                            inv.team_id = team_acc_mapp.sales_team_id.id
        return res

    @api.one
    @api.depends('invoice_line_ids.price_subtotal','invoice_line_ids.account_analytic_id.overhead_costs', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_amount(self):

        # -- deep
        # Functionality for updating "verif_tresh_exceeded" are split b/w Company & Invoice Objects

        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(line.amount for line in self.tax_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

        # Verified by Board
        if self.company_id.verify_setting < self.amount_untaxed:
            for line in self.invoice_line_ids:
                if line.account_analytic_id:
                    if line.account_analytic_id.overhead_costs == True:
                        self.verif_tresh_exceeded = True
        else:
            self.verif_tresh_exceeded = False

        # Verified by Publisher
        if (self.company_id.verify_setting < self.amount_untaxed) and (self.company_id.verify_setting_2 > self.amount_untaxed):
            for line in self.invoice_line_ids:
                if line.account_analytic_id:
                    if line.account_analytic_id.overhead_costs == True:
                        self.verif_tresh_exceeded_2 = False
                        break
                    else:
                        self.verif_tresh_exceeded_2 = True

        # If untaxed amount is greater than the both threshold , its should be verified by board
        if (self.company_id.verify_setting < self.amount_untaxed) and (self.company_id.verify_setting_2 < self.amount_untaxed):
            self.verif_tresh_exceeded = True


    @api.multi
    def action_invoice_verify_2(self):
        self.write({'state':'verified_by_publisher'})


