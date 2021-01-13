# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2016 Magnus (<http://www.magnus.nl>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'nsm_sale_advertising_order',
    'version': '1.0',
    'category': 'Sale',
    'description': """
This module allows you to use both CRM and Sales Management to run your advertising sales
=========================================================================================


    """,
    'author': 'Magnus - Willem Hulshof',
    'website': 'http://www.magnus.nl',
    'depends': [
                'sale_advertising_order',
                'nsm_ad4all_soap',
                'partner_firstname',
                'l10n_nl_partner_name',
                'report_xlsx',
                'operating_unit_report_layout',
                'report_qweb_operating_unit',
                'account_credit_control',
                'account_invoice_start_end_dates'
                ],
    'data': [
             "security/ir.model.access.csv",
             "security/groups.xml",
             "data/circulation_type.xml",
             "data/data.xml",
             "report/nsm_report.xml",
             "report/report_saleorder.xml",
             "report/report_credit_control_summary.xml",
             "views/sale_advertising_view.xml",
             "views/advertising_issue_view.xml",
             "views/product_view.xml",
             "views/circulation_type_view.xml",
             "views/proof_delivery_list_view.xml",
             "views/menuitem.xml",
             ],
    'qweb': [
    ],
    'installable': True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

