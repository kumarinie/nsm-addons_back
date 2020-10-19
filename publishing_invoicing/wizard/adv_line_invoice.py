# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from odoo.exceptions import UserError
from odoo.addons.queue_job.job import job, related_action
from odoo.addons.queue_job.exception import FailedJobError
from unidecode import unidecode

class AdOrderLineMakeInvoice(models.TransientModel):
    _inherit = "ad.order.line.make.invoice"
    _description = "Advertising Order Line Make_invoice"


    @api.multi
    def make_invoices_from_lines(self):
        """
             To make invoices.
        """
        context = self._context
        inv_date = self.invoice_date
        post_date = self.posting_date
        size = False
        eta  = False
        jq   = False
        if self.job_queue:
            jq = self.job_queue
            size = self.chunk_size
            eta = fields.Datetime.from_string(self.execution_datetime)
        if not context.get('active_ids', []):
            message = 'No ad order lines selected for invoicing.'
            if context.get('job_queue') == True :
                _logger.info(message)
                return message+"\n"
            else :
                raise UserError(_(message))
        else:
            lids = context.get('active_ids', [])
            OrderLines = self.env['sale.order.line'].browse(lids)
            invoice_date_ctx = context.get('invoice_date', False)
            posting_date_ctx = context.get('posting_date', False)
            jq_ctx = context.get('job_queue', False)
            size_ctx = context.get('chunk_size', False)
            eta_ctx = context.get('execution_datetime', False)
        if invoice_date_ctx and not inv_date:
            inv_date = invoice_date_ctx
        if posting_date_ctx and not post_date:
            post_date = posting_date_ctx
        if jq_ctx and not jq:
            jq = True
            if len(self)==1:
                self.job_queue = True
            if size_ctx and not size:
                size = size_ctx
            if eta_ctx and not eta:
                eta = fields.Datetime.from_string(eta_ctx)
        if jq:
            description = context.get('job_queue_description', False)
            if description :
                self.with_delay(eta=eta, description=description).make_invoices_split_lines_jq(inv_date, post_date, OrderLines, eta, size)
            else :
                self.with_delay(eta=eta).make_invoices_split_lines_jq(inv_date, post_date, OrderLines, eta, size)
            return "Lines dispatched for async processing. See separate job(s) for result(s).\n"
        else:
            # get list of invoicing properties and remove duplicate
            inv_property = []
            group_title_id = []
            group_advertiser_id = []
            set_invoice_property = set_group_by_title = set_customer_ids = 0
            group_by_title = []
            customer_ids = []
            for line in OrderLines:
                customer_ids.append(line.order_id.partner_id.id)
            set_customer_ids = list(set(customer_ids))
            title_count = 0
            # Loop over the customer to generate the invoice
            for cus_id in set_customer_ids:
                customer_id = self.env['res.partner'].search([('id','=',cus_id)])
                if customer_id:
                    # need to change the invoicing property based on the order line and group it
                    inv_ids = self.env['invoicing.property'].search([('id','=',customer_id.invoicing_property_id.id)])
                    
                    # -----------Group by only order--------------
                    if inv_ids.group_by_order == True and inv_ids.group_invoice_lines_per_title == False and inv_ids.group_by_advertiser == False:
                        # Loop over the selected order lines
                        for lines in OrderLines:
                            # Filter the order lines based on the customer
                            sale_order_line_id = self.env['sale.order.line'].search([('id','=',lines.id),'&',('order_partner_id','=',customer_id.id),'&',('invoicing_property_id','=',inv_ids.id),('invoice_status','!=','invoiced')])
                            if sale_order_line_id:
                                group_order = []
                                # Fetching the order number
                                for line in sale_order_line_id:
                                    group_order.append(line.order_id.id)
                                set_group_order = list(set(group_order))
                                # looping over the orders to generate invoices
                                for sale_id in set_group_order:
                                    order_line_ids = self.env['sale.order.line'].search([('id','=',lines.id),'&',('order_id','=',sale_id),'&',('order_partner_id','=',customer_id.id),'&',('invoicing_property_id','=',inv_ids.id),('invoice_status','!=','invoiced')])
                                    self.make_invoices_job_queue(inv_date, post_date, order_line_ids)
                    
                    # -------------Group by title only----------------
                    if inv_ids.group_invoice_lines_per_title == True and inv_ids.group_by_order == False and inv_ids.group_by_advertiser == False:
                        for lines in OrderLines:
                            sale_order_line_id = self.env['sale.order.line'].search([('id','=',lines.id),'&',('order_partner_id','=',customer_id.id),'&',('invoicing_property_id','=',inv_ids.id),('invoice_status','!=','invoiced')])
                            if sale_order_line_id:
                                for line in sale_order_line_id:
                                    # Fetching the title and grouping it based on the selected order lines
                                    group_title_id.append(line.title.id)
                                
                        # Removing the duplicate title ids
                        set_group_title_id = list(set(group_title_id))
                        for title_id in set_group_title_id:
                            set_group_title_order_id = []
                            group_title_order_id = []
                            for lines in OrderLines:
                                # Looping over the active order lines filtering with the Title id
                                title_order_line_ids = self.env['sale.order.line'].search(['&',('title','=',title_id),'&',('order_partner_id','=',customer_id.id),'&',('id','=',lines.id),'&',('invoicing_property_id','=',inv_ids.id),('invoice_status','!=','invoiced')])
                                if title_order_line_ids:
                                    for order_line_ids in title_order_line_ids:
                                        group_title_order_id.append(order_line_ids) 
                                set_group_title_order_id = list(set(group_title_order_id))
                            self.make_invoices_job_queue(inv_date, post_date, set_group_title_order_id)

                    # -------------Group by Advertiser and Title---------------
                    if inv_ids.group_by_advertiser == True and inv_ids.group_by_order == False and inv_ids.group_invoice_lines_per_title == True:
                        for lines in OrderLines:
                            sale_order_line_id = self.env['sale.order.line'].search([('id','=',lines.id),'&',('order_partner_id','=',customer_id.id),'&',('invoicing_property_id','=',inv_ids.id),('invoice_status','!=','invoiced')])
                            if sale_order_line_id:
                                for line in sale_order_line_id:
                                    # Fetching the title and grouping it based on the selected order lines
                                    group_title_id.append(line.title.id)
                                    group_advertiser_id.append(line.order_partner_id.id)
                        set_group_advertiser_id = list(set(group_advertiser_id))
                        set_group_title_id = list(set(group_title_id))
                        for title_id in set_group_title_id:
                            set_group_title_order_id = []
                            group_title_order_id = []
                            for advertiser_id in set_group_advertiser_id:
                                set_group_advertiser_order_id = []
                                group_advertiser_order_id = []
                                for lines in OrderLines:
                                    # Looping over the active order lines filtering with the advertiser id
                                    advertiser_order_line_ids = self.env['sale.order.line'].search(['&',('title','=',title_id),'&',('order_partner_id','=',customer_id.id),'&',('id','=',lines.id),'&',('invoicing_property_id','=',inv_ids.id),('invoice_status','!=','invoiced')])
                                    if advertiser_order_line_ids:
                                        for order_line_ids in advertiser_order_line_ids:
                                            group_advertiser_order_id.append(order_line_ids) 
                                    set_group_advertiser_order_id = list(set(group_advertiser_order_id))
                                if set_group_advertiser_order_id:
                                    # Condition is used to truncate the null value
                                    self.make_invoices_job_queue(inv_date, post_date, set_group_advertiser_order_id)

                    # -------------Group by Advertiser ---------------
                    if inv_ids.group_by_advertiser == True and inv_ids.group_by_order == False and inv_ids.group_invoice_lines_per_title == False:
                        for lines in OrderLines:
                            sale_order_line_id = self.env['sale.order.line'].search([('id','=',lines.id),'&',('order_partner_id','=',customer_id.id),'&',('invoicing_property_id','=',inv_ids.id),('invoice_status','!=','invoiced')])
                            if sale_order_line_id:
                                for line in sale_order_line_id:
                                    # Fetching the title and grouping it based on the selected order lines
                                    group_advertiser_id.append(line.order_partner_id.id)
                        set_group_advertiser_id = list(set(group_advertiser_id))
                        for advertiser_id in set_group_advertiser_id:
                            set_group_advertiser_order_id = []
                            group_advertiser_order_id = []
                            for lines in OrderLines:
                                # Looping over the active order lines filtering with the advertiser id
                                advertiser_order_line_ids = self.env['sale.order.line'].search(['&',('order_partner_id','=',customer_id.id),'&',('id','=',lines.id),'&',('invoicing_property_id','=',inv_ids.id),('invoice_status','!=','invoiced')])
                                if advertiser_order_line_ids:
                                    for order_line_ids in advertiser_order_line_ids:
                                        group_advertiser_order_id.append(order_line_ids) 
                                set_group_advertiser_order_id = list(set(group_advertiser_order_id))
                            if set_group_advertiser_order_id:
                                # Condition is used to truncate the null value
                                self.make_invoices_job_queue(inv_date, post_date, set_group_advertiser_order_id)

