# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp

class Company(models.Model):
    _inherit = 'res.company'

    verify_setting = fields.Float('Threshold 1', digits=dp.get_precision('Account'))
    verify_setting_2 = fields.Float('Threshold 2', digits=dp.get_precision('Account'))


