# -*- coding: utf-8 -*-
# Copyright 2017 Willem hulshof - <w.hulshof@magnus.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
import json
from odoo.exceptions import ValidationError

class AdvertisingIssue(models.Model):
    _inherit = "sale.advertising.issue"
    
    @api.depends('parent_id')
    @api.multi
    def _compute_medium_domain(self):
        """
        Compute the domain for the Medium domain.
        """
        for rec in self:
            if rec.parent_id:
                np = self.env.ref('sale_advertising_order.newspaper_advertising_category').id
                mag = self.env.ref('sale_advertising_order.magazine_advertising_category').id
                if np in rec.parent_id.medium.ids or mag in rec.parent_id.medium.ids:
                    ads = self.env.ref('sale_advertising_order.title_pricelist_category').id
                    rec.medium_domain = json.dumps(
                                        [('parent_id', '=', ads)]
                    )
                else:
                    ads = [self.env.ref('sale_advertising_order.online_advertising_category').id]
                    rec.medium_domain = json.dumps(
                                        [('id', 'in', ads)]
                    )
            else:
                ads = self.env.ref('sale_advertising_order.advertising_category').id
                rec.medium_domain = json.dumps(
                                    [('parent_id', '=', ads)]
                )

    medium = fields.Many2many('product.category', 'adv_issue_categ_rel', 'adv_issue_id', 'category_id', 'Medium', required=True)

    @api.onchange('parent_id')
    def onchange_parent_id(self):
        domain = {}
        self.medium = False
        if self.parent_id:
            if self.env.ref('sale_advertising_order.newspaper_advertising_category').id in self.parent_id.medium.ids:
                ads = self.env.ref('sale_advertising_order.title_pricelist_category').id
                domain['medium'] = [('parent_id', '=', ads)]
            else:
                ads = [self.env.ref('sale_advertising_order.magazine_advertising_category').id]
                ads.append(self.env.ref('sale_advertising_order.online_advertising_category').id)
                domain['medium'] = [('id', 'in', ads)]

        else:
            ads = self.env.ref('sale_advertising_order.advertising_category').id
            domain['medium'] = [('parent_id', '=', ads)]
        return {'domain': domain}

    def validate_medium(self):
        if self.parent_id:
            if len(self.medium.ids) > 1:
                raise ValidationError(_("You can't select more than one medium."))

    @api.onchange('medium')
    def _onchange_medium(self):
        self.validate_medium()

    @api.one
    @api.constrains('medium')
    def _check_medium(self):
        self.validate_medium()

    @api.multi
    def write(self, vals):
        result = super(AdvertisingIssue, self).write(vals)
        issue_date = vals.get('issue_date', False)
        if issue_date:
            issue_date = str(issue_date)
            op, ids = ('IN', tuple(self.ids)) if len(self.ids) > 1 else ('=', self.id)
            query = ("""
                    UPDATE sale_order_line 
                    SET from_date = {0},
                        to_date = {0}
                    WHERE adv_issue {1} {2}
                    """.format(
                    "'%s'" % issue_date,
                    op,
                    ids
                ))
            self.env.cr.execute(query)
        return result