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
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero

class HrExpense(models.Model):
    _inherit = 'hr.expense'

    @api.depends('sheet_id.state')
    def _get_sheet_state(self):
        for exp in self:
            if exp.sheet_id:
                exp.sheet_state = exp.sheet_id.state

    sheet_state = fields.Char(compute='_get_sheet_state', string='Sheet Status', help='Expense Report State',
                              store=True)
    state = fields.Selection(selection_add=[('revise', 'To Be Revise')])
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='WKR')

    @api.multi
    def submit_expenses(self):
        if any(expense.state != 'draft' for expense in self):
            raise UserError(_("You cannot report twice the same line!"))
        if len(self.mapped('employee_id')) != 1:
            raise UserError(_("You cannot report expenses for different employees in the same report!"))
        expense_sheet = self.env['hr.expense.sheet'].create({'expense_line_ids':[(6, 0, [line.id for line in self])], 'employee_id':self[0].employee_id.id, 'name': self[0].name if len(self.ids) == 1 else '','operating_unit_id':self[0].operating_unit_id.id})
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.expense.sheet',
            'target': 'current',
            'res_id': expense_sheet.id
        }

    @api.multi
    def view_sheet(self):
        res = super(HrExpense, self).view_sheet()
        res['flags'] = {'initial_mode': 'edit'}
        return res

    @api.multi
    def action_move_create(self):
        '''
        inherited function that is called when trying to create the accounting entries related to an expense
        '''
        res = super(HrExpense, self).action_move_create()
        for expense in self:
            if expense.analytic_account_id and expense.analytic_account_id.operating_unit_ids:
                ou = expense.analytic_account_id.operating_unit_ids[0]
                if ou and expense.sheet_id.account_move_id:
                    expense.sheet_id.account_move_id.operating_unit_id = ou.id
        return res

    def _prepare_move_line(self, line):
        move_line = super(HrExpense, self)._prepare_move_line(line)
        if self.analytic_tag_ids:
            move_line.update({'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)]})
        return move_line

    @api.multi
    def write(self, vals):
        if vals.get('operating_unit_id', False):
            sheet_id = vals['sheet_id'] if vals.get('sheet_id', False) else self.sheet_id.id
            if sheet_id:
                expense_sheet = self.env['hr.expense.sheet'].browse(sheet_id)
                expense_sheet.write({'operating_unit_id':vals.get('operating_unit_id')})
        res = super(HrExpense, self).write(vals)
        return res

    @api.onchange('analytic_account_id', 'operating_unit_id')
    def anaytic_account_change(self):
        if self.analytic_account_id and self.analytic_account_id.linked_operating_unit:
            self.operating_unit_id = self.analytic_account_id.operating_unit_ids.ids[0]


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    # Overriden:commented out @sushma
    # state = fields.Selection([('submit', 'Submitted'),
    #                           ('post', 'Posted'),
    #                           ('approve', 'Approved'),
    #                           ('done', 'Paid'),
    #                           ('cancel', 'Refused'),
    #                           ('revise', 'To Be Revise')
    #                           ], string='Status', index=True, readonly=True, track_visibility='onchange', copy=False, default='submit', required=True,
    #     help='Expense Report State')
    state = fields.Selection(selection_add=[('revise', 'To Be Revise')])



    @api.model
    def default_get(self, default_fields):
        res = super(HrExpenseSheet, self).default_get(default_fields) or {}
        res['journal_id'] = self.env.user.company_id.decl_journal_id.id
        return res


    # #Overriden:commented out @sushma
    # @api.multi
    # def approve_expense_sheets(self):
    #     if self.account_move_id:
    #         self.account_move_id.post()
    #     self.write({'state': 'approve', 'responsible_id': self.env.user.id})

    # #Overriden:commented out @sushma
    # @api.multi
    # def refuse_expenses(self, reason):
    #     if self.account_move_id:
    #         for aml in self.account_move_id.line_ids:
    #             if aml.reconciled:
    #                  raise UserError(
    #                      _('Please unreconcile payment accounting entries before cancelling this expense'))
    #         ### Then we unlink the move line
    #         self.account_move_id.button_cancel()
    #         self.account_move_id.unlink()
    #
    #     self.write({'state': 'cancel'})
    #     for sheet in self:
    #         body = (_("Your Expense %s has been refused.<br/><ul class=o_timeline_tracking_value_list><li>Reason<span> : </span><span class=o_timeline_tracking_value>%s</span></li></ul>") % (sheet.name, reason))
    #         sheet.message_post(body=body)


    # Overriden: commented out @sushma
    # @api.multi
    # def action_sheet_move_create(self):
    #     if any(sheet.state != 'submit' for sheet in self):
    #         raise UserError(_("You can only generate accounting entry for submitted expense(s)."))
    #
    #     if any(not sheet.journal_id for sheet in self):
    #         raise UserError(_("Expenses must have an expense journal specified to generate accounting entries."))
    #
    #     expense_line_ids = self.mapped('expense_line_ids')\
    #         .filtered(lambda r: not float_is_zero(r.total_amount, precision_rounding=(r.currency_id or self.env.user.company_id.currency_id).rounding))
    #
    #     res = expense_line_ids.action_move_create()
    #
    #     if not self.accounting_date:
    #         self.accounting_date = self.account_move_id.date
    #
    #     if self.payment_mode == 'own_account' and expense_line_ids:
    #         self.write({'state': 'post'})
    #     else:
    #         # self.write({'state': 'done'})
    #         self.paid_expense_sheets()
    #     return res


    # # Overriden:commented out @sushma
    # @api.multi
    # def paid_expense_sheets(self):
    #     if self.account_move_id:
    #         if not self.account_move_id.state == 'posted':
    #             self.account_move_id.post()
    #
    #     self.write({'state': 'done'})

    @api.multi
    def revise_expense(self):
        expenses = self.expense_line_ids.filtered(lambda x: x.state == 'reported')
        self.write({'state': 'revise'})
        expenses.write({'state':'revise'})

    @api.multi
    def expense_revised(self):
        expenses = self.expense_line_ids.filtered(lambda x: x.state == 'revise')
        expenses.write({'state': 'reported'})
        self.write({'state': 'approve'})

    @api.onchange('expense_line_ids')
    def onchange_expense_line_ids(self):
        if self.expense_line_ids and self.expense_line_ids[0].operating_unit_id:
            if not self.operating_unit_id or (self.operating_unit_id and len(self.expense_line_ids) == 1):
                self.operating_unit_id = self.expense_line_ids[0].operating_unit_id.id
        else:
            self.operating_unit_id = False

    @api.one
    @api.constrains('expense_line_ids', 'employee_id')
    def _check_employee(self):
        employee_ids = self.expense_line_ids.mapped('employee_id')
        group_acc_user =self.env['res.groups'].search([('name','=','Accountant')])
        is_desired_group = self.env.user.id in group_acc_user.users.ids
        # checking the state revised and group accountant
        if self.state== 'revise':
            if is_desired_group:
                # Updating the expense_line_ids with employee_id
                for emp in self.expense_line_ids:
                    emp.employee_id=self.employee_id
                return True
        if len(employee_ids) > 1 or (len(employee_ids) == 1 and employee_ids != self.employee_id):
            raise ValidationError(_('You cannot add expense lines of another employee.'))


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

