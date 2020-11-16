# -*- coding: utf-8 -*-
{
    'name': "Publishing Refunds",

    'summary': """
        Invoice Refund validation feature added for invoicing""",

    'description': """ """,
    'author': "Magnus",
    'website': "http://www.magnus.nl",

    'category': 'Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['nsm_supplier_portal','sale','account'],

    # always loaded
    'data': [
        'views/account_invoice_views.xml',
    ],
}