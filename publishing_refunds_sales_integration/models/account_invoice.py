# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountInvoice(models.Model):
	_inherit = ['account.invoice']


	@api.multi
	def action_invoice_open(self):
		res = super(AccountInvoice, self).action_invoice_open()
		for inv in self:
			if inv.type=='out_refund':
				for line in inv.invoice_line_ids:
					sale_line_id = self.env['sale.order.line'].search([('id','=',line.so_line_id.id)])
					if sale_line_id:
						for sale_line in sale_line_id:
							sale_line.qty_invoiced = sale_line.qty_invoiced - line.quantity
							# when validated a refund invoice, reference is added in sale order line - invoice_lines
							sale_line.invoice_lines = [(4, line.id)]
		return res

