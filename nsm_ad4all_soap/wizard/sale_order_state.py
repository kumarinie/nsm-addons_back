# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError
# from odoo.addons.queue_job.job import job, related_action
from odoo.addons.queue_job.exception import FailedJobError

class SaleOrderAd4all(models.TransientModel):
    """
    This wizard will update all the selected orders in Ad4all
    """

    _name = "sale.order.ad4all"
    _description = "Update the selected sale orders in Ad4all"


    def sale_order_update_ad4all(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        orders = self.env['sale.order'].browse(active_ids)
        for order in orders:
            if order.state not in ('sale') or not order.advertising:
                raise UserError(
                        _("Selected order(s) cannot be updated to Ad4all as "
                          "they are not in 'Sale', or 'Done' state"
                          " or they are not Advertising Orders."))
        orders.with_delay().action_ad4all('update', False)
        return {'type': 'ir.actions.act_window_close'}




