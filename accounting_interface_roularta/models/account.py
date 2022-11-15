from odoo import api, fields, models, _
from datetime import datetime, date
from odoo import exceptions
import base64
from odoo.addons.queue_job.job import job, related_action
from odoo.addons.queue_job.exception import FailedJobError
import xmltodict
import requests
from requests.auth import HTTPBasicAuth
from odoo.exceptions import UserError


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

    roularta_log_id = fields.Many2one(
        'move.odooto.roularta',
        copy=False
    )

    @api.multi
    def action_cancel(self):
        res = super(AccountInvoice, self).action_cancel()
        self.invoice_line_ids.write({'roularta_sent': False})
        return res
    @job
    @api.multi
    def action_roularta_interface(self):
        for inv in self:
            sale_invoice = inv.invoice_line_ids.mapped('sale_order_id')
            vendor_bill = inv.invoice_line_ids.mapped('purchase_id')
            if sale_invoice or vendor_bill:
                res = inv.transfer_invoice_to_roularta()
                res.with_delay(
                    description=res.invoice_name
                ).roularta_content()

    @api.multi
    def transfer_invoice_to_roularta(self):
        self.ensure_one()
        if self.roularta_sent:
            vals = {
                'invoice_id': self.id,
                'invoice_name': self.name,
                'reference': 'This Invoice will not be sent to Roularta',
            }
            res = self.env['move.odooto.roularta'].sudo().create(vals)
            return res
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
                'date':datetime.strptime(self.date_invoice, '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S.000')

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
                    'due_date':datetime.strptime(mline.date, '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S'),
                    'media_code':'BI',
                    'user_ref1':UserRef1,
                    'user_ref2':'',
                    'ExtRef1':'',
                    'ExtRef2':'',
                    'ExtRef6':'',
                }
                summary_lines.append((0, 0, lvals))
                summary_seq += 1

            # Analysis line
            for mline in self.move_id.line_ids.\
                    filtered(lambda ml: ml.credit > 0 and ml.account_id not in invoice_tax_account):
                aa_code = mline.analytic_account_id and str(mline.analytic_account_id.code)

                taxes = mline.tax_ids.compute_all(mline.credit, mline.currency_id,
                                                  mline.quantity, mline.product_id, mline.partner_id)['taxes']
                total_tax_amount = 0.0
                for tax in taxes:
                    total_tax_amount += tax['amount']

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
                    'due_date': datetime.strptime(mline.date, '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S'),
                    'code': 'VFL21',
                    'short_name': 'Verkoopfacturen locaal 21',
                    'ExtRef4': '<![CDATA[G&RBR]]>',
                    'description': '<![CDATA[Geld ? Recht Teaserbox Nieuwsbrief]]>',
                    'value': total_tax_amount,
                }
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
                    'due_date': datetime.strptime(mline.date, '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S'),
                }
                summary_lines.append((0, 0, lvals))
                summary_seq += 1

            vals['roularta_invoice_line'] = summary_lines
            res = self.env['move.odooto.roularta'].sudo().create(vals)
            return res

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        self.action_roularta_interface()
        return res


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    roularta_sent = fields.Boolean(
        'Invoice Line sent to Roularta',
        copy=False
    )

class MovefromOdootoRoularta(models.Model):
    _name = 'move.odooto.roularta'
    _order = 'create_date desc'
    _rec_name = 'number'

    @api.depends('roularta_invoice_line.roularta_response')
    @api.multi
    def _compute_response(self):
        for acc in self:
            acc.account_roularta_response = True
            for line in acc.roularta_invoice_line:
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
        string='Roularta Response'
    )
    xml_message = fields.Text(
        'XML message'
    )

    @job
    def roularta_content(self, xml=False):
        self.ensure_one()
        if self.account_roularta_response:
            raise UserError(_(
                'This Account Invoice already has been succesfully sent to Roularta.'))
        if self.roularta_invoice_line:
            response = self.roularta_invoice_line.call_roularta(self, xml)
            if response.status_code == 200:
                self.env['account.invoice.line'].search(
                    [('invoice_id', '=', self.invoice_id.id)]).write(
                    {'roularta_sent': True})
            else:
                return
        acc = self.env['account.invoice'].search(
            [('id', '=', self.invoice_id.id)])
        accvals = {'date_sent_roularta': datetime.now(),
                  'roularta_log_id': self.id,
                  }
        acc.write(accvals)
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
    roularta_response = fields.Integer(
        'Roularta Response'
    )
    roularta_response_message = fields.Text(
        'Reply message'
    )

    def call_roularta(self, inv, xml=False):
        config = self.env['roularta.config'].search([], limit=1)
        url = str(config.host)
        user = str(config.username)
        pwd = str(config.password)

        xmlDict = {
            'soapenv:Envelope': {
                '@xmlns:soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
                '@xmlns:web': 'http://www.coda.com/efinance/schemas/inputext/input-14.0/webservice',
                '@xmlns:tran': 'http://www.coda.com/efinance/schemas/transaction',
                '@xmlns:flex': 'http://www.coda.com/common/schemas/flexifield',
                '@xmlns:att': 'http://www.coda.com/common/schemas/attachment',
                '@xmlns:inp': 'http://www.coda.com/efinance/schemas/inputext',
                '@xmlns:mat': 'http://www.coda.com/efinance/schemas/matching',
                '@xmlns:ass': 'http://www.coda.com/efinance/schemas/association',
                'soapenv:Header': {
                    'web:Options': {
                        '@user': config.username,
                        '@company': inv.company_code,
                    }
                },
                'soapenv:Body': {
                    'web:PostOptions': {
                        '@postto': "anywhere"
                    },
                    'web:PostRequest': {
                        'Transaction': {
                            'trans:Header': {
                                '@xmlns:trans': 'http://www.coda.com/efinance/schemas/transaction',
                                'trans:Key': {
                                    'trans:CmpCode': inv.company_code,
                                    'trans:Code': "VFAV",
                                    'trans:Number': inv.number
                                },
                                'trans:Period': inv.period,
                                'trans:CurCode': inv.curcode.name,
                                'trans:Date': datetime.strptime(inv.date, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S')
                            },
                            'trans:Lines': {
                                '@xmlns:trans':'http://www.coda.com/efinance/schemas/transaction',
                                'trans:Line':[]
                            }
                        }
                    }
                }
            }
        }
        
        transaction_lines = []
        for line in self:
            entry = {
                    'trans:Number':line.number,
                    'trans:DestCode':line.dest_code,
                    'trans:AccountCode':line.account_code,
                    'trans:DocValue':line.doc_value,
                    'trans:DualRate':line.dual_rate,
                    'trans:DocRate':line.doc_rate,
                    'trans:LineType':line.line_type,
                    'trans:LineSense':line.line_sense,
                    'trans:LineOrigin':line.line_origin,
                    'trans:DueDate':datetime.strptime(line.due_date, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S'),
            }

            if line.line_type == 'summary':
                entry.update({
                    'trans:DocSumTax':line.doc_sum_tax,
                    'trans:MediaCode':line.media_code,
                    'trans:UserRef1':line.user_ref1 or '',
                    'trans:UserRef2':line.user_ref2 or '',
                    'trans:ExtRef1':line.ext_ref1 or '',
                    'trans:ExtRef2':line.ext_ref2 or '',
                    'trans:ExtRef6':line.ext_ref6 or '',

                })
            elif line.line_type == 'analysis':
                entry.update({
                    # 'trans:TaxInclusive':False,
                    'trans:TaxInclusive':'',
                    'trans:ExtRef4':'<![CDATA[G&RBR]]>',
                    'trans:Description':'<![CDATA[Geld ? Recht Teaserbox Nieuwsbrief]]>',
                    'trans:Taxes':{
                        'trans:Tax':{
                            'trans:Code':line.code,
                            'trans:ShortName':line.short_name,
                            'trans:Value':line.value,
                        }
                    },
                })

            elif line.line_type == 'tax':
                entry.update({
                    'trans:TaxLineCode':line.code,
                    'trans:DocTaxTurnover':line.doc_tax_turnover
                })

            transaction_lines.append(entry)

        xmlDict['soapenv:Envelope']['soapenv:Body']['web:PostRequest']['Transaction']['trans:Lines']['trans:Line'] = transaction_lines

        xmlData = xmltodict.unparse(xmlDict, pretty=True, full_document=False)

        headers = {
            'SOAPAction': 'uri-coda-webservice/14.000.0030/finance/Input/Post',
            'Content-Type': 'application/xml',
        }

        try:
            response = requests.request("POST", url, headers=headers, data=str(xmlData), auth=HTTPBasicAuth(user, pwd))

            self.write({
                'roularta_response': response.status_code,
                'roularta_response_message': response.text,
            })
            inv.write({'xml_message': str(xmlData)})
        except Exception as e:
            raise FailedJobError(
                _('Error Roularta Interface call: %s') % (e))
        return response



