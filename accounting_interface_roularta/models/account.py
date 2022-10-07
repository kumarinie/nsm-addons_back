from odoo import api, fields, models, _
from datetime import datetime, date
from odoo import exceptions

from xml.dom import minidom, Node



# <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:web="http://www.coda.com/efinance/schemas/inputext/input-14.0/webservice" xmlns:tran="http://www.coda.com/efinance/schemas/transaction" xmlns:flex="http://www.coda.com/common/schemas/flexifield" xmlns:att="http://www.coda.com/common/schemas/attachment" xmlns:inp="http://www.coda.com/efinance/schemas/inputext" xmlns:mat="http://www.coda.com/efinance/schemas/matching" xmlns:ass="http://www.coda.com/efinance/schemas/association">
# <soapenv:Header>
# <web:Options user="INTERFACE" company="NRMN">
# </web:Options>
# </soapenv:Header>


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.depends('invoice_line_ids.roularta_sent')
    @api.multi
    def _roularta_sent(self):
        for inv in self:
            inv.roularta_sent = False
            for line in inv.invoice_line_ids:
                if line.roularta_sent:
                    inv.roularta_sent = True
                    break

    roularta_sent = fields.Boolean(
        compute=_roularta_sent,
        string='Invoice Line sent to Roularta',
        default=False,
        store=True,
        copy=False
    )

    date_sent_roularta = fields.Datetime(
        'Datetime Sent to roularta',
        index=True,
        copy=False,
        help="Datetime on which Invoice is sent to roularta."
    )

    publog_id = fields.Many2one(
        'move.odooto.roularta',
        copy=False
    )

    # @job
    @api.multi
    def action_roularta_interface(self, arg):
        for inv in self:
            sale_invoice = inv.invoice_line_ids.mapped('sale_order_id')
            vendor_bill = inv.invoice_line_ids.mapped('purchase_id')
            if sale_invoice or vendor_bill:
                inv.transfer_invoice_to_roularta(arg)

    @api.multi
    def transfer_invoice_to_roularta(self, arg):
        self.ensure_one()
        if self.roularta_sent:
            vals = {
                'invoice_id': self.id,
                'invoice_name': self.name,
                'reference': 'This Invoice will not be sent to Roularta',
            }
            res = self.env['move.odooto.roularta'].sudo().create(vals)
        else:
            vals = {
                'invoice_id':self.id,
                'invoice_name': self.name,
                'reference': self.number,
                'move_id':self.move_id.id,
                'company_code':self.operating_unit_id.code,
                'code':'XXX',
                'number':self.number,
                'period':datetime.strptime(self.date_invoice, '%Y-%m-%d').strftime('%Y/%m'),
                'curcode':self.currency_id.id,
                # 'date':datetime.strptime(self.date_invoice, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S.000')
                'date':datetime.strptime(self.date_invoice, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S.000')

            }

            summary_seq = 1
            invoice_tax_account = self.tax_line_ids.mapped('account_id')
            tax_lines = self.move_id.line_ids.filtered(lambda ml: ml.account_id in invoice_tax_account)
            tax_amt = sum(tl.credit for tl in tax_lines)
            sale_invoice = self.invoice_line_ids.mapped('sale_order_id')
            vendor_invoice = self.invoice_line_ids.mapped('purchase_id')

            move_line = self.env['move.line.odooto.roularta']
            summary_lines=[]
            operating_code = self.operating_unit_id.code

            #Summary line
            for mline in self.move_id.line_ids.filtered(lambda ml: ml.debit > 0):
                UserRef1 = self.number
                if sale_invoice:
                    UserRef1 = 'V' + UserRef1
                elif vendor_invoice:
                    UserRef1 = 'I' + UserRef1

                lvals = {
                    'move_line_id': mline.id,
                    'number':summary_seq,
                    'dest_code':operating_code,
                    'account_code':mline.account_id.code + '.' + mline.partner_id.ref,
                    'doc_value':mline.debit-tax_amt,
                    'doc_sum_tax':tax_amt,
                    'dual_rate':40.339900000,
                    'doc_rate':1.000000000,
                    'line_type':'summary',
                    'line_sense':"debit" if sale_invoice else "credit",
                    'line_origin':'dl_orig_additional',
                    'due_date':datetime.strptime(mline.date, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S'),
                    'media_code':'BI',
                    'user_ref1':UserRef1,
                    'user_ref2':'',
                    'ExtRef1':'',
                    'ExtRef2':'',
                    'ExtRef6':'',
                }
                # move_line.sudo().create(lvals)
                summary_lines.append((0, 0, lvals))
                summary_seq += 1

            # Analysis line
            for mline in self.move_id.line_ids.\
                    filtered(lambda ml: ml.credit > 0 and ml.account_id not in invoice_tax_account):
                # print '------------------------'
                # print type(str(mline.analytic_account_id.code))
                aa_code = mline.analytic_account_id and str(mline.analytic_account_id.code)

                taxes = mline.tax_ids.compute_all(mline.credit, mline.currency_id,
                                                  mline.quantity, mline.product_id, mline.partner_id)['taxes']
                total_tax_amount = 0.0
                for tax in taxes:
                    total_tax_amount += tax['amount']

                # print taxes,total_tax_amount
                lvals = {
                    'move_line_id': mline.id,
                    'number': summary_seq,
                    'dest_code': operating_code,
                    'account_code': mline.account_id.code + '.' + mline.partner_id.ref + '.' + aa_code + '.' + mline.product_id.default_code,
                    'doc_value': mline.credit,
                    'dual_rate': 40.339900000,
                    'doc_rate': 1.000000000,
                    'line_type': 'analysis',
                    'line_sense': "credit" if sale_invoice else "debit",
                    'line_origin': 'dl_orig_additional',
                    'due_date': datetime.strptime(mline.date, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S'),
                    'code': 'VFL21',
                    'short_name': 'Verkoopfacturen locaal 21',
                    'ExtRef4': '<![CDATA[G&RBR]]>',
                    'description': '<![CDATA[Geld ? Recht Teaserbox Nieuwsbrief]]>',
                    'value': total_tax_amount,
                }
                # move_line.sudo().create(lvals)
                summary_lines.append((0, 0, lvals))
                summary_seq += 1

            # Tax line
            for tax_line in self.tax_line_ids:
                mline = self.move_id.line_ids.filtered(lambda ml: ml.credit > 0 and ml.account_id.id == tax_line.account_id.id)
                lvals = {
                    'move_line_id': mline.id,
                    'number': summary_seq,
                    'dest_code': operating_code,
                    'account_code': tax_line.account_id.code,
                    'doc_value': tax_line.amount,
                    'dual_rate': 40.339900000,
                    'doc_rate': 1.000000000,
                    'line_type': 'tax',
                    'line_sense': "credit" if sale_invoice else "debit",
                    'line_origin': 'dl_orig_gentax',
                    'code':'VFL21',
                    'due_date': datetime.strptime(mline.date, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S'),
                }
                # move_line.sudo().create(lvals)
                summary_lines.append((0, 0, lvals))
                summary_seq += 1

            vals['roularta_invoice_line'] = summary_lines
            print vals
            res = self.env['move.odooto.roularta'].sudo().create(vals)
            return True

        

    def soap_tag_parsing(self):
        config = self.env['roularta.config'].search([])
        invoice_tax_account = self.tax_line_ids.mapped('account_id')
        tax_lines = self.move_id.line_ids.filtered(lambda ml: ml.account_id in invoice_tax_account)
        operating_code = self.operating_unit_id.code

        header = '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" ' \
                      'xmlns:web="http://www.coda.com/efinance/schemas/inputext/input-14.0/webservice" ' \
                      'xmlns:tran="http://www.coda.com/efinance/schemas/transaction" ' \
                      'xmlns:flex="http://www.coda.com/common/schemas/flexifield" ' \
                      'xmlns:att="http://www.coda.com/common/schemas/attachment" ' \
                      'xmlns:inp="http://www.coda.com/efinance/schemas/inputext" ' \
                      'xmlns:mat="http://www.coda.com/efinance/schemas/matching" ' \
                      'xmlns:ass="http://www.coda.com/efinance/schemas/association">'+\
                      '<web:Options user="INTERFACE" company="%s">'%config.name+\
                      '</web:Options></soapenv:Header>'


        body = '<soapenv:Body>' \
                    '<web:PostOptions postto="anywhere"> </web:PostOptions>' \
                    '<web:PostRequest>' \
                    '<Transaction>' \
                    '<trans:Header xmlns:trans="http://www.coda.com/efinance/schemas/transaction">' \
                    '<trans:Key>' \
                    '<trans:CmpCode>%s</trans:CmpCode>' \
                    '<trans:Code>%s</trans:Code>' \
                    '<trans:Number>%s</trans:Number>' \
                    '</trans:Key>' \
                    '<trans:Period>%s</trans:Period>' \
                    '<trans:CurCode>%s</trans:CurCode>' \
                    '<trans:Date>%s</trans:Date>' \
                    '</trans:Header>'%\
                    (operating_code, 'VFAV', self.number,
                     datetime.strptime(self.date_invoice, '%Y-%m-%d').strftime('%Y/%m'),
                     self.currency_id.name,
                     datetime.strptime(self.date_invoice, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S.000'))

        summary_seq = 1
        tax_amt = sum(tl.credit for tl in tax_lines)
        sale_invoice = self.invoice_line_ids.mapped('sale_order_id')
        vendor_invoice = self.invoice_line_ids.mapped('purchase_id')

        lines = '<trans:Lines xmlns:trans="http://www.coda.com/efinance/schemas/transaction">'
        for mline in self.move_id.line_ids.filtered(lambda ml: ml.debit > 0):
            UserRef1 = self.number
            if sale_invoice:
                UserRef1 ='V'+UserRef1
            elif vendor_invoice:
                UserRef1 = 'I' + UserRef1

            summary_line =  '<trans:Line>' \
                            '<trans:Number>%s</trans:Number>' \
                            '<trans:DestCode>%s</trans:DestCode>' \
                            '<trans:AccountCode>%s</trans:AccountCode>' \
                            '<trans:DocValue>%s</trans:DocValue>' \
                            '<trans:DocSumTax>%s</trans:DocSumTax>' \
                            '<trans:DualRate>40.339900000</trans:DualRate>' \
                            '<trans:DocRate>1.000000000</trans:DocRate>' \
                            '<trans:LineType>summary</trans:LineType>' \
                            '<trans:LineSense>%s</trans:LineSense>' \
                            '<trans:LineOrigin>dl_orig_additional</trans:LineOrigin>' \
                            '<trans:DueDate>%s</trans:DueDate>' \
                            '<trans:MediaCode>BI</trans:MediaCode>' \
                            '<trans:UserRef1>%s</trans:UserRef1>' \
                            '<trans:UserRef2></trans:UserRef2>' \
                            '<trans:ExtRef1></trans:ExtRef1>' \
                            '<trans:ExtRef2></trans:ExtRef2>' \
                            '<trans:ExtRef6></trans:ExtRef6>' \
                            '</trans:Line>'%(
                                summary_seq,
                                operating_code,
                                mline.account_id.code+'.'+mline.partner_id.ref,
                                mline.debit-tax_amt,
                                tax_amt,
                                "debit" if sale_invoice else "credit",
                                datetime.strptime(mline.date, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S'),
                                UserRef1,
                             )

            lines += summary_line

        for mline in self.move_id.line_ids.\
                filtered(lambda ml: ml.credit > 0 and ml.account_id not in invoice_tax_account):
            print '------------------------'
            print type(str(mline.analytic_account_id.code))
            aa_code = mline.analytic_account_id and str(mline.analytic_account_id.code)

            summary_seq += 1
            analysis_line ='<trans:Line>'\
                            '<trans:Number>%s</trans:Number>' \
                            '<trans:DestCode>%s</trans:DestCode>' \
                            '<trans:AccountCode>%s</trans:AccountCode>'\
                            '<trans:DocValue>%s</trans:DocValue>' \
                            '<trans:LineSense>%s</trans:LineSense>' \
                            '<trans:LineType>analysis</trans:LineType>' \
                            '<trans:LineOrigin>dl_orig_additional</trans:LineOrigin>'\
                            '<trans:TaxInclusive>false</trans:TaxInclusive>' \
                            '<trans:DualRate>40.339900000</trans:DualRate>'\
                            '<trans:DocRate>1.000000000</trans:DocRate>'\
                            '<trans:ExtRef4><![CDATA[G&RBR]]></trans:ExtRef4>'\
                            '<trans:Description><![CDATA[Geld ? Recht Teaserbox Nieuwsbrief]]></trans:Description>'\
                            '<trans:DueDate>%s</trans:DueDate>'\
                            '<trans:Taxes>'\
                            '<trans:Tax>'\
                            '<trans:Code>VFL21</trans:Code>'\
                            '<trans:ShortName>Verkoopfacturen locaal 21</trans:ShortName>'\
                            '<trans:Value>157.5</trans:Value>'\
                            '</trans:Tax>'\
                            '</trans:Taxes>'\
                            '</trans:Line>'%(
                                summary_seq,
                                operating_code,
                                mline.account_id.code + '.' + mline.partner_id.ref+'.' +aa_code+'.'+mline.product_id.default_code,
                                mline.credit,
                                "credit" if sale_invoice else "debit",
                                datetime.strptime(mline.date, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S'),
                            )
            lines += analysis_line

        for mline in self.move_id.line_ids. \
                filtered(lambda ml: ml.credit > 0 and ml.account_id in invoice_tax_account):
            summary_seq += 1
            tax_line = '<trans:Line>'\
                '<trans:Number>%s</trans:Number>'\
                '<trans:DestCode>%s</trans:DestCode>'\
                '<trans:AccountCode>%s</trans:AccountCode>'\
                '<trans:DocValue>%s</trans:DocValue>'\
                '<trans:DocRate>1.000000000</trans:DocRate >'\
                '<trans:DualRate>40.339900000</trans:DualRate>'\
                '<trans:LineSense>%s</trans:LineSense>'\
                '<trans:LineType>tax</trans:LineType>'\
                'trans:LineOrigin>dl_orig_gentax</trans:LineOrigin>'\
                '<trans:TaxLineCode>VFL21</trans:TaxLineCode>'\
                '<trans:DocTaxTurnover>%s</trans:DocTaxTurnover>'\
                '<trans:DueDate>%s</trans:DueDate>'\
                '</trans:Line>'%(
                    summary_seq,
                    operating_code,
                    mline.account_id.code,
                    mline.credit,
                    "debit" if sale_invoice else "credit",
                    'analysis tax amount',
                    datetime.strptime(mline.date, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S'),
            )

            lines += tax_line

        lines += '</trans:Lines>'\
                '</Transaction>'\
                '</web:PostRequest>'\
                '</soapenv:Body>'\
                '</soapenv:Envelope>'

        response_code =''

        response_ok = '<soapenv:Envelope xmlns:soapenv = "http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd = "http://www.w3.org/2001/XMLSchema" xmlns:xsi = "http://www.w3.org/2001/XMLSchema-instance">'\
                        '<soapenv:Body>'\
                        '<webservice:PostResponse xmlns:webservice = "http://www.coda.com/efinance/schemas/inputext/input-14.0/webservice" ' \
                        'xmlns = "http://www.coda.com/efinance/schemas/inputext" ' \
                        'xmlns:com = "http://www.coda.com/efinance/schemas/common" ' \
                        'xmlns:atc = "http://www.coda.com/common/schemas/attachment" '\
                        'xmlns:mat = "http://www.coda.com/efinance/schemas/matching" '\
                        'xmlns:itm = "http://www.coda.com/efinance/schemas/inputtemplate"'\
                        'xmlns:ffd = "http://www.coda.com/common/schemas/flexifield"'\
                        'xmlns:elm = "http://www.coda.com/efinance/schemas/elementmaster"'\
                        'xmlns:doc = "http://www.coda.com/efinance/schemas/documentmaster"'\
                        'xmlns:inp = "http://www.coda.com/efinance/schemas/input"'\
                        'xmlns:txn = "http://www.coda.com/efinance/schemas/transaction"'\
                        'xmlns:aso = "http://www.coda.com/efinance/schemas/association">'\
                        '<webservice:Key>'\
                        '<txn:CmpCode>%s</txn:CmpCode >'\
                        '<txn:Code>VFAV</txn:Code>'\
                        '<txn:Number>%s</txn:Number>'\
                        '</webservice:Key>'\
                        '</webservice:PostResponse>'\
                        '</soapenv:Body>'\
                        '</soapenv:Envelope>'%(
                            operating_code,
                            response_code
                        )


        response_nok = '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'\
                        '<soapenv:Body>'\
                        '<soapenv:Fault>'\
                        '<faultcode>soapenv:Client</faultcode>'\
                        '<faultstring>The document header VFAV with number %s already exists. Failed to create a document header for document VFAV with number 2230397.</faultstring>'\
                        '<detail>'\
                        '<ns1:Reason xmlns:ns1="http://www.coda.com/efinance/schemas/common">'\
                        '<ns1:Text code="WSADAPTER_EMSG_MESSAGE">The document header VFAV with number %s already exists.</ns1:Text>'\
                        '<ns1:Text code="WSADAPTER_EMSG_MESSAGE">Failed to create a document header for document VFAV with number %s.</ns1:Text>'\
                        '</ns1:Reason>'\
                        '</detail>'\
                        '</soapenv:Fault>'\
                        '</soapenv:Body>'\
                        '</soapenv:Envelope>'%(
                            response_code,
                            response_code,
                            response_code
                        )


        lines += response_ok + response_nok




        # print '---------soap_header---------',soap_header
        # print '---------soap_header---------',soap_body
        print '---------line---------',lines
        # print '---------soap_debit_line---------',analysis_line

        raise Exception("bus.Bus only string channels are allowed.")

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    roularta_sent = fields.Boolean(
        'Invoice Line sent to Roularta',
        copy=False
    )




class MovefromOdootoRoularta(models.Model):
    _name = 'move.odooto.roularta'
    _order = 'create_date desc'

    @api.depends('roularta_invoice_line.roularta_response')
    @api.multi
    def _compute_response(self):
        for acc in self:
            acc.account_roularta_response = True
            for line in acc.ad4all_so_line:
                if line.roularta_response != 200:
                    acc.account_roularta_response = False
                    break

    invoice_id = fields.Many2one(
        'account.invoice',
        "Invoice"
    )
    move_id = fields.Many2one(related='invoice_id.move_id', relation="account.move", string='Move', store=True, readonly=True)
    company_code = fields.Char('Company Code', size=16)
    code = fields.Char('Code', size=16)
    number = fields.Char('Invoice Number')
    period = fields.Char('Period', size=16)
    curcode = fields.Many2one('res.currency','CurCode')
    date = fields.Datetime('Date')
    invoice_name = fields.Char('Invoice Description')
    reference = fields.Char('Invoice Reference')
    roularta_invoice_line = fields.One2many(
        'move.line.odooto.roularta',
        'inv_id',
        string='Invoice Lines',
        copy=False
    )
    account_roularta_response = fields.Boolean(
        compute=_compute_response,
        default=False,
        store=True,
        string='Ad4all Response'
    )

    # @job
    def wsdl_content(self, xml=False):
        self.ensure_one()
        if self.account_roularta_response:
            raise UserError(_(
                'This Account Invoice already has been succesfully sent to Roularta.'))
        if self.roularta_invoice_line:
            response = self.roularta_invoice_line.call_wsdl(xml)
            if response['code'] == 200:#need to check this parameter
                self.env['account.invoice.line'].search(
                    [('invoice_id', '=', self.invoice_id.id)]).write(
                    {'roularta_sent': True})
            else:
                return
        acc = self.env['account.invoice'].search(
            [('id', '=', self.invoice_id.id)])
        accvals = {'date_sent_roularta': datetime.datetime.now(),
                  'publog_id': self.id,
                  # 'ad4all_tbu': False
                  }
        acc.write(accvals)
        # wsdl = "http://trial.ad4all.nl/data/wsdl"
        # self.so_ad4all_environment = wsdl
        return True




class MoveLinefromOdootoRoularta(models.Model):
    _name = 'move.line.odooto.roularta'
    _order = 'create_date desc'

    move_line_id = fields.Many2one('account.move.line', "Move Line")
    number = fields.Integer(string='Sequence Number')
    dest_code = fields.Char(string='Dest Code', size=16)
    account_code = fields.Char(string='Account Code', size=64)
    doc_value = fields.Float(string='DocValue')
    doc_sum_tax = fields.Float(string='DocSumTax')
    dual_rate = fields.Float(string='Dual Rate')
    doc_rate = fields.Float(string='Doc Rate')
    line_type = fields.Char(string='Line Type', size=16)
    line_sense = fields.Char(string='Line Sense', size=16)
    line_origin = fields.Char(string='Line Origin', size=32)
    due_date = fields.Datetime('Due Date', size=16)
    media_code = fields.Char('Media Code', size=16)
    user_ref1 = fields.Char('User Ref1', size=16)
    user_ref2 = fields.Char('User Ref2', size=16)
    ext_ref1 = fields.Char('Ext Ref1', size=16)
    ext_ref2 = fields.Char('Ext Ref2', size=16)
    ext_ref4 = fields.Char('Ext Ref4', size=16)
    ext_ref6 = fields.Char('Ext Ref6', size=16)
    description = fields.Char('Description', size=64)
    code = fields.Char('Code', help="Analysis code/ Tax line code!", size=16)
    short_name = fields.Char('Short Name', size=32)
    value = fields.Float('Value', help='Tax amount for this line!')
    doc_tax_turnover = fields.Float(string='Doc Tax Turnover')
    inv_id = fields.Many2one(
        'move.odooto.roularta',
        string='invoice_from_Reference',
        ondelete='cascade',
        required=True,
        copy=False
    )
    roularta_response = fields.Text(
        'Roularta Response'
    )

    def call_wsdl(self, xml=False):
        config = self.env['roularta.config'].search([], limit=1)
        client = config.check_connection()
        # client = Client(
        #     wsdl,
        #     transport=Transport(session=session),
        #     settings=settings,
        #     plugins=[history]
        # )
        
        
        Order = client.type_factory('ns0')
        order_obj = Order.order(
            portal="nsm_L8hd6Ep",
            deliverer="nsm",
            order_code=int(float(self.adgr_orde_id.id))
        )
        # paper_deadline = datetime.datetime.strptime(
        #     self.paper_deadline, '%Y-%m-%d').strftime('%Y%m%d') \
        #     if self.paper_deadline else ''
        # paper_pub_date = datetime.datetime.strptime(
        #     self.paper_pub_date, '%Y-%m-%d').strftime(
        #     '%Y%m%d') if self.paper_pub_date else ''

        doc = minidom.Document()

        #Soap header
        header_envelope = doc.createElement('soapenv:Envelope')
        doc.appendChild(header_envelope)
        header_envelope.setAttribute('xmlns:ass', 'http://www.coda.com/efinance/schemas/association')
        header_envelope.setAttribute('xmlns:mat', 'http://www.coda.com/efinance/schemas/matching')
        header_envelope.setAttribute('xmlns:inp', 'http://www.coda.com/efinance/schemas/inputext')
        header_envelope.setAttribute('xmlns:att', 'http://www.coda.com/common/schemas/attachment')
        header_envelope.setAttribute('xmlns:flex', 'http://www.coda.com/common/schemas/flexifield')
        header_envelope.setAttribute('xmlns:trans', 'http://www.coda.com/efinance/schemas/transaction')
        header_envelope.setAttribute('xmlns:web', 'http://www.coda.com/efinance/schemas/inputext/input-14.0/webservice')
        header_envelope.setAttribute('xmlns:soapenv', 'http://schemas.xmlsoap.org/soap/envelope/')

        header_soap_header = doc.createElement('soapenv:Header')
        header_envelope.appendChild(header_soap_header)

        header_web_option = doc.createElement('web:Options')
        header_web_option.setAttribute('company', config.name)
        header_web_option.setAttribute('user', "INTERFACE")
        header_web_option.appendChild(doc.createTextNode(''))
        header_soap_header.appendChild(header_web_option)


        #soap body
        soap_body = doc.createElement('soapenv:Body')
        header_envelope.appendChild(soap_body)
        body_post_option = doc.createElement('web:PostOptions')
        body_post_option.setAttribute('postto', "anywhere")
        body_post_option.appendChild(doc.createTextNode(''))
        soap_body.appendChild(body_post_option)

        body_transaction = doc.createElement('Transaction')
        soap_body.appendChild(body_transaction)

        body_header = doc.createElement('trans:Header')
        body_header.setAttribute('xmlns:trans', "http://www.coda.com/efinance/schemas/transaction")
        soap_body.appendChild(body_header)

        body_header_key = doc.createElement('trans:key')
        body_header.appendChild(body_header_key)

        body_key_vals = doc.createElement('trans:CmpCode')
        body_header_key.appendChild(body_key_vals)
        body_key_vals.appendChild(doc.createTextNode(self.inv_id.company_code))



        xmlData = dicttoxml(xml_dict, attr_type=False, root=False)
        xmlData = (xmlData.replace('<item>', '')).replace('<item >', '').replace('</item>', '')
        order_obj.xml_data = xmlpprint(xmlData)
        try:
            response = client.service.soap_order(order=order_obj)
            self.write({
                'ad4all_response': response['code'],
                'json_message': order_obj.xml_data,
        })
        except Exception as e:
            raise FailedJobError(
                _('Error wsdl call: %s') % (e))
        return response



