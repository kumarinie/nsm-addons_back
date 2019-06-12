# -*- coding: utf-8 -*-
{
    'name': "NSM Clickable many2one fields for tree views",

    'summary': """
        Open the linked resource when clicking on their name""",

    'description': """
        For the widget option, you need to add widget="many2one_clickable" attribute in the XML field definition in the tree view.

        For example:
        
        <field name="partner_id" widget="many2one_clickable" />
        
        will open the linked partner in a form view.
        
        If system parameter web_tree_many2one_clickable.default is true and you need to disable one field, then use widget="many2one_unclickable"
    """,
    'author': "Magnus - Willem Hulshof",
    'website': "http://www.magnus.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['web_tree_many2one_clickable', 'nsm_sale_advertising_order'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_advertising_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}