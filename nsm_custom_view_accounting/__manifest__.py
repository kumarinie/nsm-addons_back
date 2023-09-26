# -*- coding: utf-8 -*-
# Copyright 2018 Willem Hulshof Magnus (www.magnus.nl).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "nsm_custom_view_accounting",

    'summary': """
        This module creates custom form view for Vendor Bills menu.""",

    'description': """
        This module creates custom form view for Vendor Bills menu.
    """,

    'author': "Magnus",
    'website': "http://www.magnus.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'other',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['nsm_account',
                'account_operating_unit',
                'account_invoice_transmit_method'],

    # always loaded
    'data': [
        'views/account_invoice_view.xml',
    ],
}
