# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductCategory(models.Model):
    _inherit = 'product.category'

    adv_pro_type_ids = fields.Many2many('advertising.product.matrix', string='Advertising Product Types')