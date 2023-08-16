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

{
    'name': 'NSM Leveranciers Portaal',
    'version': '1.0',
    'category': 'Invoice',
    'summary': 'NSM Leveranciers Portaal',
    'description': """
    New Skool Media Leveranciers Portaal.
    * New Skool Media Leveranciers Portaal uitbreiding.
    """,
    'author': 'BAS Solutions',
    'website': 'https://www.bas-solutions.nl',
    'depends': ['base', 'account', 'mail',
                'portal', 'sale_crm',
                'account_invoice_2step_validation',
                'stock',
                'nsm_account',
                'account_invoice_supplier_ref_unique',
                'account_invoice_check_total',
                ],
    'data': [
        "data/data.xml",
        "data/auth_signup_send_mail_data.xml",

        "security/supplier_portal_security_view.xml",
        "security/ir.model.access.csv",

        "views/mail_thread_view.xml",
        "views/res_partner_view.xml",
        "views/account_invoice_view.xml",
        "views/product_view.xml",
        "views/account_analytic_view.xml",
        "views/menu_view.xml",
        "views/res_config_view.xml",
        "views/res_company_view.xml",
        "views/sales_team_view.xml",

        "wizard/generate_mapping_view.xml",
        "views/res_bank_view.xml",
        "views/portal_wizard_view.xml",
    ],
    'demo': [],
    'test': [
    ],
    'qweb': [
        'static/src/xml/mail.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
