# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2014 BAS Solutions
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
import json

class Invoice(models.Model):
    _inherit = 'account.invoice'

    @api.one
    def _get_file(self):

        attach = self.env['ir.attachment'].search([('res_id', '=', self.id),
                                    ('res_model', '=', self._name)], order='id desc', limit=1)
        self.file = attach.datas or False
        self.data_file = attach.name

    @api.one
    def _set_file(self):
        return True

    @api.one
    def _get_supp_file(self):
        Company = self.env['res.company']._company_default_get('account.invoice')
        self.supplier_terms = Company.supplier_terms

    @api.one
    def _set_supp_file(self):
        return True

    @api.one
    def _get_SupplierReference(self):
        self.supplier_ref_related = self.supplier_invoice_number

    @api.model
    def _get_terms(self):
        Company = self.env['res.company']._company_default_get('account.invoice')
        if Company.supplier_terms:
            return Company.supplier_terms
        return False

    @api.model
    def _get_term_file_name(self):
        Company = self.env['res.company']._company_default_get('account.invoice')
        if Company.supplier_terms and Company.data_fname:
            return Company.data_fname
        return False

    @api.model
    def _get_supplier(self):
        user = self.env.user
        return user.partner_id.id

    @api.model
    def _get_reference_type(self):
        return [('none', _('Free Reference'))]

    @api.model
    def _default_currency(self):
        return super(Invoice, self)._default_currency()


    @api.model
    def _default_journal(self):
        return super(Invoice, self)._default_journal()


    supplier_id = fields.Many2one('res.partner', 'Supplier', default=_get_supplier)
    main_account_analytic_id = fields.Many2one('account.analytic.account', 'Main Analytic account',
                                               domain=[('portal_main', '=', True)])

    sub_account_analytic_id = fields.Many2one('account.analytic.account', 'Sub Analytic account')
    is_portal = fields.Boolean('Portal')

    data_supplier_terms_file_name = fields.Char('File Name', default=_get_term_file_name)
    supplier_terms = fields.Binary(compute='_get_supp_file',
                                   inverse='_set_supp_file', default=_get_terms,
                                   string="Supplier Invoice Reuse-authorization File")

    is_submitted = fields.Boolean('Submitted')
    supplier_ref_related = fields.Char(compute='_get_SupplierReference', string='Supplier Reference')
    avail_supplier_portal = fields.Selection([('marketing', 'Marketing'),
                                               ('editorial', 'Editorial')],
                                              "Available Supplier Portal",)

    data_file = fields.Char(compute='_get_file', inverse='_set_file', string='File Name')
    file = fields.Binary(compute='_get_file', inverse='_set_file', string="Upload Your Invoice")

    terms = fields.Boolean('I accept the re-use terms')
    reuse = fields.Boolean('Reuse')

    product_category = fields.Many2one('product.category', 'Cost Category',domain=[('parent_id.supportal', '=', True)])


    state = fields.Selection([
        ('portalcreate','Portal Create'),
        ('draft','Draft'),
        ('start_wf', 'Start Workflow'),
        ('proforma','Pro-forma'),
        ('proforma2','Pro-forma'),
        ('open','Open'),
        ('auth','Authorized'),
        ('verified','Verified'),
        ('paid','Paid'),
        ('cancel','Cancelled'),
        ],'Status', index=True, readonly=True, track_visibility='onchange',

        default=lambda self: self._context.get('state', 'draft'),
        help='* The \'Portal Create\' status is used when a Portal user is encoding a new and unconfirmed Invoice, before it gets submitted. \
        \n* The \'Draft\' status is used when a user is encoding a new and unconfirmed Invoice. \
        \n* The \'Pro-forma\' when invoice is in Pro-forma status,invoice does not have an invoice number. \
        \n* The \'Authorized\' status is used when invoice is already posted, but not yet confirmed for payment. \
        \n* The \'Verified\' status is used when invoice is already authorized, but not yet confirmed for payment, because it is of higher value than Company Verification treshold. \
        \n* The \'Open\' status is used when user create invoice,a invoice number is generated.Its in open status till user does not pay invoice. \
        \n* The \'Paid\' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled. \
        \n* The \'Cancelled\' status is used when user cancel invoice.')

    name = fields.Char(string='Reference/Description', index=True,
        readonly=True, states={'draft':[('readonly',False)],'start_wf':[('readonly',False)],'portalcreate':[('readonly',False)]},
        copy=False, help='The name that will be used on account move lines')

    origin = fields.Char(string='Source Document',
        help="Reference of the document that produced this invoice.",
        readonly=True, states={'draft': [('readonly', False)],'start_wf':[('readonly',False)]})

    move_name = fields.Char(string='Journal Entry Name', readonly=True,
        default=False, copy=False, states={'draft':[('readonly',False)],'start_wf':[('readonly',False)],'portalcreate':[('readonly',False)]},
        help="Technical field holding the number given to the invoice, automatically set when the invoice is validated then stored to set the same number again if the invoice is cancelled, set to draft and re-validated.")

    supplier_invoice_number = fields.Char(
            string='Vendor invoice number',
            readonly=True, help="The reference of this invoice as provided by the supplier.",
            states={'draft':[('readonly',False)],'start_wf':[('readonly',False)],'portalcreate':[('readonly',False)]},
            copy=False)

    reference_type = fields.Selection('_get_reference_type', string='Payment Reference',
        required=True, readonly=True, states={'draft':[('readonly',False)],'start_wf':[('readonly',False)],'portalcreate':[('readonly',False)]},
        default='none')
    date_invoice = fields.Date(string='Invoice Date',
        readonly=True, states={'draft':[('readonly',False)],'start_wf':[('readonly',False)],'portalcreate':[('readonly',False)]}, index=True,
        help="Keep empty to use the current date", copy=False)
    date_due = fields.Date(string='Due Date',
        readonly=True, states={'draft':[('readonly',False)],'start_wf':[('readonly',False)],'portalcreate':[('readonly',False)]}, index=True, copy=False,
        help="If you use payment terms, the due date will be computed automatically at the generation "
             "of accounting entries. The payment term may compute several due dates, for example 50% "
             "now and 50% in one month, but if you want to force a due date, make sure that the payment "
             "term is not set on the invoice. If you keep the payment term and the due date empty, it "
             "means direct payment.")

    partner_id = fields.Many2one('res.partner', string='Partner', change_default=True,
        required=True, readonly=True, states={'draft':[('readonly',False)],'start_wf':[('readonly',False)],'portalcreate':[('readonly',False)]},
        track_visibility='always')

    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', oldname='payment_term',
        readonly=True, states={'draft':[('readonly',False)],'start_wf':[('readonly',False)],'portalcreate':[('readonly',False)]},
        help="If you use payment terms, the due date will be computed automatically at the generation "
             "of accounting entries. If you keep the payment term and the due date empty, it means direct payment. "
             "The payment term may compute several due dates, for example 50% now, 50% in one month.")

    account_id = fields.Many2one('account.account', string='Account',
        required=True, readonly=True, states={'draft':[('readonly',False)],'start_wf':[('readonly',False)],'portalcreate':[('readonly',False)]},
        domain=[('deprecated', '=', False)], help="The partner account used for this invoice.")

    invoice_line_ids = fields.One2many('account.invoice.line', 'invoice_id', string='Invoice Lines', oldname='invoice_line',
        readonly=True, states={'draft':[('readonly',False)],'start_wf':[('readonly',False)],'portalcreate':[('readonly',False)]}, copy=True)
    tax_line_ids = fields.One2many('account.invoice.tax', 'invoice_id', string='Tax Lines', oldname='tax_line',
        readonly=True, states={'draft':[('readonly',False)],'start_wf':[('readonly',False)],'portalcreate':[('readonly',False)]}, copy=True)

    currency_id = fields.Many2one('res.currency', string='Currency',
        required=True, readonly=True, states={'draft':[('readonly',False)],'start_wf':[('readonly',False)],'portalcreate':[('readonly',False)]},
        default=_default_currency, track_visibility='always')

    journal_id = fields.Many2one('account.journal', string='Journal',
        required=True, readonly=True, states={'draft':[('readonly',False)],'start_wf':[('readonly',False)],'portalcreate':[('readonly',False)]},
        default=_default_journal,
        domain="[('type', 'in', {'out_invoice': ['sale'], 'out_refund': ['sale'], 'in_refund': ['purchase'], 'in_invoice': ['purchase']}.get(type, [])), ('company_id', '=', company_id)]")

    company_id = fields.Many2one('res.company', string='Company', change_default=True,
        required=True, readonly=True, states={'draft':[('readonly',False)],'start_wf':[('readonly',False)],'portalcreate':[('readonly',False)]},
        default=lambda self: self.env['res.company']._company_default_get('account.invoice'))

    check_total = fields.Float('Verification Total', digits=dp.get_precision('Account'), readonly=True,
                               states={'draft':[('readonly',False)],'start_wf':[('readonly',False)],'portalcreate':[('readonly',False)]})
    partner_bank_id = fields.Many2one('res.partner.bank', string='Bank Account',
        help='Bank Account Number to which the invoice will be paid. A Company bank account if this is a Customer Invoice or Vendor Refund, otherwise a Partner bank account number.',
        readonly=True, states={'draft':[('readonly',False)],'start_wf':[('readonly',False)],'portalcreate':[('readonly',False)]})

    user_id = fields.Many2one('res.users', string='Salesperson', track_visibility='onchange',
        readonly=True, states={'draft':[('readonly',False)],'start_wf':[('readonly',False)],'portalcreate':[('readonly',False)],'open':[('readonly',False)]},
        default=lambda self: self.env.user)

    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position', oldname='fiscal_position',
        readonly=True, states={'draft':[('readonly',False)],'start_wf':[('readonly',False)],'portalcreate':[('readonly',False)]})

    topf = fields.Boolean('To Portal Flow', readonly=True, states={'draft':[('readonly',False)],'start_wf':[('readonly',False)]}, help="Checking makes routing to Portal Flow possible")


    @api.onchange('supplier_id', 'company_id')
    def supplier_id_change(self):
        res = {}
        if not self.supplier_id:
            return res

        res = {'value': {
                'partner_id': self.supplier_id.id,
                'reuse': self.supplier_id.reuse,
                'is_portal': True,
                }}

        return res

    @api.onchange('product_category')
    def product_category_change(self):
        res = {}
        llist = []
        if not self.product_category:
            return res

        for line in self.invoice_line_ids:
            if line.product_id:
                llist.append((1, line.id, {'product_id': [],}))
        if llist:
            res = {'value': {'invoice_line_ids': llist },
                   'warning': {'title': 'Let op!', 'message': 'U heeft de Factuurcategorie aangepast. Nu moet u opnieuw product(-en) en Edities/Kostenplaatsen selecteren in de factuurregel(s)'}}
        return res

    @api.onchange('main_account_analytic_id')
    def onchange_main_analytic_ac(self):
        res, llist = {}, []
        if not self.main_account_analytic_id:
            return res

        for line in self.invoice_line_ids:
            if line.account_analytic_id:
                llist.append((1, line.id, {'account_analytic_id': [],}))

        if llist:
            res = { 'value': { 'invoice_line_ids': llist },
                    'warning': {'title': 'Let op!', 'message': 'U heeft de Titel/Afdeling aangepast. Nu moet u opnieuw Edities/Kostenplaatsen selecteren in de factuurregel(s)'}}

        operating_unit_ids = self.main_account_analytic_id.operating_unit_ids
        if len(operating_unit_ids) > 1:
            res['domain'] = {'operating_unit_id':[('id','in',operating_unit_ids.ids)]}
        else:
            res['domain'] = {'operating_unit_id':[('id','in',operating_unit_ids.ids)]}
            res['value'] = {'operating_unit_id':operating_unit_ids.ids[0]}
        return res


    @api.multi
    def action_portal_submit(self):
        salesTeam = self.env['sales.team']

        for case in self:
            if not case.file:
                raise UserError(_('Please Upload your invoice File before submit.'))

            if case.reuse and not case.terms:
                raise UserError(_('Please Accept re-use terms'))

            if not case.invoice_line_ids:
                raise UserError(_('Please create some invoice lines.'))

            if str(case.check_total) != str(case.amount_total):
                raise UserError(_('Please make sure Verification Total is equal to Invoice Total.'))

            salesTeam = salesTeam.search(
                        [('analytic_account_id', '=', case.main_account_analytic_id.id),
                          ('product_cat_id', '=', (case.invoice_line_ids and
                                                   case.invoice_line_ids[0].product_id.categ_id and
                                                   case.invoice_line_ids[0].product_id.categ_id.id or False)) or False
                         ], limit=1)

            case.write({'is_portal': True,
                        'date_invoice': fields.Date.context_today(self),
                        'state': 'start_wf',
                        # 'section_id': salesTeam.sales_team_id.id,
                        'team_id':  salesTeam.sales_team_id.id,
                        'user_id':  salesTeam.sales_team_id.user_id.id or self.env.user.id})
            # self.button_reset_taxes(cr, uid, ids, context=context)

        return True


    @api.multi
    def action_portalback(self):
        cr = self._cr

        for case in self:
            cr.execute('SELECT create_uid FROM account_invoice WHERE id=%s', (case.id,))
            res_user_id = cr.fetchone()
            [res_user_obj] = self.env['res.users'].browse([res_user_id[0]])

            if not case.supplier_id or case.supplier_id is not case.partner_id:
                if not res_user_obj.partner_id or res_user_obj.partner_id.id is not case.partner_id.id:
                    self.write({'state':'portalcreate','is_portal': False, 'topf': True,
                                 'supplier_id': case.partner_id.id})
                else:
                    self.write({'state':'portalcreate','is_portal': False, 'supplier_id': case.partner_id.id})

            if not res_user_obj.partner_id or res_user_obj.partner_id.id is not case.partner_id.id:
                self.write({'state':'portalcreate','is_portal': False, 'topf': True })
            else:
                self.write({'state':'portalcreate','is_portal': False })
        return True


    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """
        Overrides orm field_view_get.
        @return: Dictionary of Fields, arch and toolbar.
        """
        res = {}
        res = super(Invoice, self).fields_view_get(view_id=view_id, view_type=view_type,
                                                    toolbar=toolbar, submenu=submenu)
        if not self._context.get('is_portal'):
            return res
        res['toolbar'] = {'print': [], 'other': []}
        return res

    # --deep
    @api.multi
    def _add_followers_notify(self):
        """
            Adding followers of Partner to Invoice
        """
        self.ensure_one()
        mappedPartner = map(lambda x: x.partner_id.id, self.message_follower_ids)

        PartnerIDs = []
        for mf in self.partner_id.message_follower_ids:
            if mf.partner_id.id in mappedPartner: continue
            PartnerIDs.append(mf.partner_id.id)

        if not PartnerIDs:
            return False

        mail_invite = self.env['mail.wizard.invite'].with_context({
            'default_res_model': self._name,
            'default_res_id': self.id}).create({
            'partner_ids': [(4, PartnerIDs)], 'send_mail': True})
        return mail_invite.add_followers()


    def _force_update_file(self, vals):
        try: self.ensure_one()
        except: return False

        attachment = self.env['ir.attachment']
        attachment.create({'datas': vals.get('file', ''),
                         'datas_fname': vals.get('data_file','/'),
                         'name': vals.get('data_file','/'),
                         'res_id': self.id, 'res_model': self._name,
                         'type': 'binary'
                        })


    @api.model
    def create(self, vals):
        res = super(Invoice, self).create(vals)
        res._add_followers_notify()

        # Force Set File
        if 'data_file' in vals and vals.get('data_file', False):
            res._force_update_file(vals)

        return res

    @api.multi
    def write(self, vals):
        res = super(Invoice, self).write(vals)

        # Force Set File
        if 'data_file' in vals and vals.get('data_file', False):
            self._force_update_file(vals)

        return res



class InvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.depends('product_id')
    @api.multi
    def _compute_acc_analytic_domain(self):
        """
        Compute the domain for the account_analytic_id domain.
        """
        for rec in self:
            if rec.invoice_id.main_account_analytic_id:
                parent_adv_issues = rec.env['sale.advertising.issue'].search([('analytic_account_id', '=', rec.invoice_id.main_account_analytic_id.id), ('parent_id', '=', False)])
                child_adv_issues = rec.env['sale.advertising.issue'].search([('parent_id', 'in', parent_adv_issues.ids)])
                analytic_ids = child_adv_issues.mapped('analytic_account_id').ids
                if rec.invoice_id.main_account_analytic_id:
                    rec.acc_analytic_domain = json.dumps(
                        [('id', '=', analytic_ids)]
                    )
            else:
                rec.acc_analytic_domain = json.dumps(
                        [('id', '=', [])]
                    )

    new_tax_id = fields.Many2one('account.tax', 'Tax',)
    acc_analytic_domain = fields.Char(compute=_compute_acc_analytic_domain, readonly=True, store=False, )

    @api.onchange('new_tax_id')
    def onchange_tax_id(self):
        if not self.new_tax_id:
            return {'value': {'invoice_line_tax_ids': []}}
        return {'value': {'invoice_line_tax_ids': [(6, 0, [self.new_tax_id.id])]}}


    @api.onchange('product_id')
    def _onchange_product_id(self):

        res = super(InvoiceLine, self)._onchange_product_id()

        if not self._context.get('is_portal'):
            return res

        vals = res.get('value', {})
        res['value'] = vals
        iltax = self.invoice_line_tax_ids.ids
        self.new_tax_id = iltax and iltax[0] or False

        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
