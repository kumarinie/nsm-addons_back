from odoo import api, fields, models, _
from datetime import datetime, date

class RoulartaConfig(models.Model):
    _name = "roularta.config"
    _description = 'Roularta Config'
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
    # msg = fields.Char(string="Connection Message", copy=False)

    # @api.multi
    # def check_connection(self):
    #     self.ensure_one()
    #     msg = ''
    #     client =''
    #     try:
    #         session = Session()
    #         user = self.username
    #         password = self.password
    #         session.auth = HTTPBasicAuth(user, password)
    #         settings = Settings(strict=False, xml_huge_tree=True)
    #         wsdl = self.host
    #         history = HistoryPlugin()
    #         client = Client(
    #             wsdl,
    #             transport=Transport(session=session),
    #             settings=settings,
    #             plugins=[history]
    #         )
    #         msg = 'Successfully connected to Roularta Interface'
    #     except Exception, msg:
    #         msg
    #     self.write({'msg': msg})
    #     self._cr.commit()
    #     return client

