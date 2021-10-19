# -*- coding: utf-8 -*-
from odoo import http

# class StopInvoiceFollwerMail(http.Controller):
#     @http.route('/stop_invoice_follwer_mail/stop_invoice_follwer_mail/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stop_invoice_follwer_mail/stop_invoice_follwer_mail/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stop_invoice_follwer_mail.listing', {
#             'root': '/stop_invoice_follwer_mail/stop_invoice_follwer_mail',
#             'objects': http.request.env['stop_invoice_follwer_mail.stop_invoice_follwer_mail'].search([]),
#         })

#     @http.route('/stop_invoice_follwer_mail/stop_invoice_follwer_mail/objects/<model("stop_invoice_follwer_mail.stop_invoice_follwer_mail"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stop_invoice_follwer_mail.object', {
#             'object': obj
#         })