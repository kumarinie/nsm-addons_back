# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountInvoice(models.Model):
	_inherit = ['account.invoice']

	modify_refund_created = fields.Boolean(string="Modified refund created using this invoice")


	@api.multi
	def action_invoice_open(self):
		res = super(AccountInvoice, self).action_invoice_open()
		# Below field is used to avoid the multiple invoice id to sale_order_line.invoice_line
		for inv in self:
			for line in inv.invoice_line_ids:
				sale_line_id = self.env['sale.order.line'].search([('id','=',line.so_line_id.id)])

				if sale_line_id:
					for sale_line in sale_line_id:
						if inv.type =='out_invoice':
							sale_line.invoice_lines = [(4, line.id)]
						if inv.type == 'out_refund':
							sale_line.invoice_lines = [(4, line.id)]
					#fetch the invoice lines to add the removed lines from standard 
						inv_line_ids = self.env['account.invoice.line'].search([('so_line_id','=',sale_line.id)])
						for inv_line in inv_line_ids:
							if inv_line.invoice_id.state != 'cancel':
								sale_line.invoice_lines = [(4, inv_line.id)]
		return res

