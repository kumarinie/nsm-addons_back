# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013 - 2018 Magnus - Willem Hulshof - www.magnus.nl
#
#
##############################################################################

{
    'name' : 'nsm_account_invoice_2step_validation',
    'version' : '0.9',
    'category': 'accounts',
    'description': """
This module adds authorization steps in workflow in nsm supplier invoices.
=============================================================================

Enchanced to add
* Authorization
* Verification status on the Invoice

    """,
    'author'  : 'Magnus - Willem Hulshof',
    'website' : 'http://www.magnus.nl',
    'depends' : ['account_invoice_2step_validation',
                 # 'nsm_supplier_portal',
                 'sales_team',
    ],
    'data' : [
        "security/account_security.xml",
        "views/res_partner_view.xml",
        "views/account_invoice_view.xml",
        "views/account_analytic_view.xml",
        "views/user_view.xml",
        "views/res_company_view.xml"
    ],
    'demo' : [],
    'installable': True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

