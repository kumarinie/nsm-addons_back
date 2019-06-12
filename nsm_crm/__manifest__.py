# -*- coding: utf-8 -*-
{
    'name': "nsm_crm",

    'summary': """
        This module adds enhancement to crm module""",

    'description': """
        This module adds enhancement to crm module
    """,

    'author': "Magnus - Willem Hulshof",
    'website': "http://www.magnus.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale_advertising_order', 'partner_sector', 'partner_firstname'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_partner_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}