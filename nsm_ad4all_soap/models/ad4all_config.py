from odoo import api, fields, models, _
from datetime import datetime, date

class ad4allConfig(models.Model):
    _name = "ad4all.config"
    _description = 'Ad4all Config'
    _rec_name = 'username'

    # name = fields.Char('Company Code', required=True)
    host = fields.Char('URL', required=True,
        help='This is the URL that the system can be reached at.'
    )
    username = fields.Char('Username', required=True,
        help='This is the username that is used for authenticating to this '
             'system, if applicable.',
    )
    password = fields.Char('Password', required=True,
        help='This is the password that is used for authenticating to this '
             'system, if applicable.',
    )
