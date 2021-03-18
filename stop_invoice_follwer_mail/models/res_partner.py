# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Partner(models.Model):
    _inherit = 'res.partner'

    stop_followers_mail = fields.Boolean("No Follower Invite Emails")