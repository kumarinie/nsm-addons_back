# -*- coding: utf-8 -*-
{
    'name': "nsm_package",

    'summary': """
        Package Sale & Accounting""",

    'description': """
        
    """,

    'author': 'Magnus - Willem Hulshof',
    'website': 'http://www.magnus.nl',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sale & Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale','package_sale_advertising_order', 'nsm_account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        "report/report_saleorder.xml",
        'report/report_invoice.xml',
        'views/sale_views.xml',        
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}