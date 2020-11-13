# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountInvoice(models.Model):
	_inherit = ['account.invoice']


	@api.multi
	def action_invoice_open(self):
		res = super(AccountInvoice, self).action_invoice_open()
		# Below field is used to avoid the multiple invoice id to sale_order_line.invoice_line
		updated_sale_inv_id = 0
		for inv in self:
			if inv.type == 'out_refund':
				for line in inv.invoice_line_ids:
					sale_line_id = self.env['sale.order.line'].search([('id','=',line.so_line_id.id)])
					if sale_line_id:
						for sale_line in sale_line_id:
							if sale_line.qty_invoiced != line.quantity:
								if sale_line.qty_invoiced > line.quantity:
									sale_line.qty_invoiced = sale_line.qty_invoiced - line.quantity
									updated_sale_inv_id = 1
								else:
									updated_sale_inv_id = 0

							if sale_line.price_unit != line.price_unit:
								if sale_line.price_unit > line.price_unit:
									sale_line.price_unit = sale_line.price_unit - line.price_unit
									updated_sale_inv_id = 1
								else:
									updated_sale_inv_id = 0
									
							# when validated a refund invoice, reference is added in sale order line - invoice_lines
							if updated_sale_inv_id == 1:
								sale_line.invoice_lines = [(4, line.id)]
			if inv.type == 'out_invoice':
				for line in inv.invoice_line_ids:
					sale_line_id = self.env['sale.order.line'].search([('id','=',line.so_line_id.id)])
					if sale_line_id:
						for sale_line in sale_line_id:
							if sale_line.qty_invoiced != line.quantity:
								sale_line.qty_invoiced = line.quantity
								updated_sale_inv_id = 1
							else:
								updated_sale_inv_id = 0

							if sale_line.price_unit != line.price_unit:
								sale_line.price_unit = line.price_unit
								updated_sale_inv_id = 1
							else:
								updated_sale_inv_id = 0
							# when validated a revised invoice, reference is added in sale order line - invoice_lines
							if updated_sale_inv_id == 1:
								sale_line.invoice_lines = [(4, line.id)]
		return res

