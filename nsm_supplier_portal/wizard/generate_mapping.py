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

class GenerateMapping(models.TransientModel):
    _name = 'generate.mapping'
    _description = 'Generate Sales Team Mapping'

    state = fields.Selection(
            [('draft', 'Draft'), ('generated', 'Generated')], 'State',
            default='draft')
    existing_generated = fields.Integer('Existing',)
    new_create = fields.Integer('New Created')
    total = fields.Integer('Total')


    
    def generate_mapping(self):
        context = self._context
        user = self.env.user

        company_id = context.get('company_id', user.company_id.id)
        analytic_ac_pool = self.env['account.analytic.account']
        product_category_pool = self.env['product.category']
        sales_team_pool = self.env['sales.team']
        existing_counter = 0
        created_counter = 0
        total = 0

        analytic_search_ids = analytic_ac_pool.search([('portal_main', '=',  True),
                                                       '|',('company_id','=', company_id),('company_id','=', False)])

        product_cat_ids = product_category_pool.search([('parent_id.supportal', '=', True)])

        view_ref = self.env['ir.model.data'].get_object_reference('nsm_supplier_portal', 'section_sales_department1')
        view_id = view_ref and view_ref[1] or False,

        for analytic_obj in analytic_search_ids:
            for product_cat_obj in product_cat_ids:
                existing_search = sales_team_pool.search(
                    [('analytic_account_id', '=', analytic_obj.id),
                      ('product_cat_id', '=', product_cat_obj.id)])
                if existing_search:
                    existing_counter +=1
                    continue
                sales_team_pool.create({'analytic_account_id': analytic_obj.id,
                                        'product_cat_id': product_cat_obj.id,
                                        'sales_team_id': view_id and view_id[0] or False,
                                        })
                created_counter +=1
        total = existing_counter + created_counter
        self.write({'state': 'generated',
                  'existing_generated': existing_counter,
                  'new_create': created_counter,
                  'total': total,
                 })
        return {
            'name': _('Generate Sales Team Mapping'),
            'type': 'ir.actions.act_window',
            'res_model': 'generate.mapping',
            'res_id': self._ids[0],
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'nodestroy': True,
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
