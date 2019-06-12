# -*- encoding: utf-8 -*-

# Copyright 2018 Willem Hulshof Magnus (www.magnus.nl).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "nsm_custom_view_sales",

    'summary': """
        This module creates custom views for NSM sales menus.""",

    'description': """
        This module creates custom views for NSM sales menus.
    """,

    'author': "Magnus - Lucie Bolt",
    'website': "http://www.magnus.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['nsm_sale_advertising_order',
                ],

    # always loaded
    'data': [
        'views/nsm_adv_order_line_tree_view.xml',
    ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

