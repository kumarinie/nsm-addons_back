# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AdvertisingIssue(models.Model):
    _inherit = 'sale.advertising.issue'

    adv_pro_type_ids = fields.Many2many('advertising.product.matrix', string='Advertising Product Types')