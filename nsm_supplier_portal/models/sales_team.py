# -*- coding: utf-8 -*-


from odoo import api, fields, models, _

class SalesTeam(models.Model):
    _name = 'sales.team'
    _description = 'Sales Team Mapping'
    _rec_name = 'name'

    
    def concate_name(self):
        """concate name of product category and analytic account"""
        self.name = self.analytic_account_id.name.strip() + ' / ' + self.product_cat_id.name.strip()

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    product_cat_id = fields.Many2one('product.category', 'Product Category',)
    name = fields.Char(compute='concate_name', string='Name', store=True, size=64)

    sales_team_id = fields.Many2one('crm.team', 'Sales Team',)
    company_id = fields.Many2one('res.company', 'Company', required=True, change_default=True,
                                 default=lambda self: self.env['res.company']._company_default_get('account.invoice'))

    _sql_constraints = [
        ('analytic_prodt_cat_id_uniq', 'unique (analytic_account_id, product_cat_id)',
         'The combination of Analytic account and Product Category must be unique!'),
        ]



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
