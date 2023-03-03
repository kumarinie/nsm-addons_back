from odoo import api, fields, models, _

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    adv_pro_type_ids = fields.Many2many('advertising.product.matrix', compute='_compute_ad_issue_pro_type', string='Advertising Issue Pro Type')

    @api.multi
    @api.depends('ad_class')
    def _compute_ad_issue_pro_type(self):
        for ol in self:
            ad_class_pro_type = ol.ad_class.adv_pro_type_ids
            ol.adv_pro_type_ids = ad_class_pro_type and ad_class_pro_type.ids
