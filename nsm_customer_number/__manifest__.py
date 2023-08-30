# -*- coding: utf-8 -*-
{
    'name': "nsm_customer_number",

    'summary': """
        This module provides a readonly field for the legacy number of Newskoolmedia customers. 
        It also moves the field "ref" to the header of the res.partner form """,

    'description': """
        This module provides a readonly field for the legacy code for nsm customers. 
    """,

    'author': "W. Hulshof",
    'website': "http://www.tosc.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'integration',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'views/res_partner_view.xml',
    ],
    'external_dependencies': {
    },
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}