# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError


class AccountInvoiceRefund(models.TransientModel):
	"""Refunds invoice"""

	_inherit = "account.invoice.refund"
	_description = "Invoice Refund"


	@api.multi
	def compute_refund(self, mode='refund'):
		res = super(AccountInvoiceRefund,self).compute_refund()
		inv_obj = self.env['account.invoice']
		inv_line_obj = self.env['account.invoice.line']
		context = dict(self._context or {})

		for form in self:
			for inv in inv_obj.browse(context.get('active_ids')):
				if inv.type=='out_invoice':
					for lines in inv.invoice_line_ids:
						if not lines.sale_line_ids:
							raise UserError(_(' You cannot refund the invoice which doesnt have a relation to sale order!!'))
		return res
