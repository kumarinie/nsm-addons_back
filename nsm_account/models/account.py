# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ['account.move', 'mail.thread']

    @api.multi
    def _track_subtype(self, init_values):
        if 'state' in init_values and self.state == 'draft':
            return 'nsm_account.mt_move_unposted'

        if 'state' in init_values and self.state == 'posted':
            return 'nsm_account.mt_move_posted'

        return super(AccountMove, self)._track_subtype(init_values)

    @api.multi
    def _get_default_journal1(self):
        return super(AccountMove, self)._get_default_journal()


    state = fields.Selection([('draft', 'Unposted'), ('posted', 'Posted')], string='Status',
      required=True, readonly=True, copy=False, default='draft', track_visibility='onchange',
      help='All manually created new journal entries are usually in the status \'Unposted\', '
           'but you can set the option to skip that status on the related journal. '
           'In that case, they will behave as journal entries automatically created by the '
           'system on document validation (invoices, bank statements...) and will be created '
           'in \'Posted\' status.')

    journal_id = fields.Many2one('account.journal', string='Journal', track_visibility='onchange',
                                 required=True, states={'posted': [('readonly', True)]},
                                 default=_get_default_journal1)

    @api.multi
    def button_cancel(self):
        for move in self:
            if not move.journal_id.update_posted:
                raise UserError(_('You cannot modify a posted entry of this journal.\nFirst you should set the journal to allow cancelling entries.'))
        if self.ids:
            self._check_lock_date()
            # self._cr.execute('UPDATE account_move '\
            #            'SET state=%s '\
            #            'WHERE id IN %s', ('draft', tuple(self.ids),))
            self.write({'state': 'draft'})
            self.invalidate_cache()
        self._check_lock_date()
        return True



class AnalyticAccount(models.Model):
    _inherit = "account.analytic.account"


    # date_publish = fields.Date('Publishing Date')
    code = fields.Char('Reference', index=True, required=True, track_visibility='onchange')
    # section_ids = fields.Many2many('crm.team','analytic_section_rel','analytic_account_id','section_id','Sales Teams')
    department_id = fields.Many2one('hr.department', 'Department')

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Code Analytic Account must be unique!'),
    ]


    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            account_ids = self.search([('code', '=ilike', name + "%")] + args, limit=limit)
            if not account_ids:
                dom = []
                for name2 in name.split('/'):
                    name = name2.strip()
                    account_ids = self.search(dom + [('name', operator, name)] + args, limit=limit)
                    if not account_ids: break
                    dom = [('parent_id','in',account_ids.ids)]
        else:
            account_ids = self.search(args, limit=limit)
        return account_ids.name_get()



class AnalyticAccountLine(models.Model):
    _inherit = "account.analytic.line"

    partner_id = fields.Many2one(related='move_id.partner_id', relation="res.partner", string='Partner', store=True, readonly=True)






# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
