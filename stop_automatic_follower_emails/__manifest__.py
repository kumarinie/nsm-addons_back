# -*- coding: utf-8 -*-
{
    'name': "stop_automatic_follower_emails",

    'summary': """
        Stop invoice auto follower mail
        """,

    'description': """
        Stop invoice auto follower mail
    """,

    'author': "Magnus-K.Sushma",
    'website': "http://www.magnus.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Discuss',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['nsm_supplier_portal', 'follower_mails_configuration'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}