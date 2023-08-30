# -*- coding: utf-8 -*-
from odoo import http

# class AccountingInterfaceRoularta(http.Controller):
#     @http.route('/accounting_interface_roularta/accounting_interface_roularta/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/accounting_interface_roularta/accounting_interface_roularta/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('accounting_interface_roularta.listing', {
#             'root': '/accounting_interface_roularta/accounting_interface_roularta',
#             'objects': http.request.env['accounting_interface_roularta.accounting_interface_roularta'].search([]),
#         })

#     @http.route('/accounting_interface_roularta/accounting_interface_roularta/objects/<model("accounting_interface_roularta.accounting_interface_roularta"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('accounting_interface_roularta.object', {
#             'object': obj
#         })