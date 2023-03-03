# -*- coding: utf-8 -*-
{
    'name': "Advertising Product Matrix",

    'summary': """
        Advertising Matrix Type""",

    'description': """
        Advertising Matrix Type
    """,

    'author': "K.Sushma",
    'website': "http://www.tosc.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['digital_domain_sale_advertising_order'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/advertising_product_matrix_views.xml',
        'views/advertising_issue_views.xml',
        'views/product_views.xml',
        'views/sale_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}