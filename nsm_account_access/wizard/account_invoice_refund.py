# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class AccountInvoiceRefund(models.TransientModel):
    """Refunds invoice"""

    _inherit = "account.invoice.refund"

    @api.multi
    def compute_refund(self, mode='refund'):
        ctx = self.env.context.copy()
        if self.env.user.has_group('sale_advertising_order.group_traffic_user'):
            ctx.update({'allow_user':True})
        return super(AccountInvoiceRefund, self.with_context(ctx)).compute_refund(mode)