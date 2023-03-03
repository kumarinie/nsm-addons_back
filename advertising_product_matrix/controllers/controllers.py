# -*- coding: utf-8 -*-
from odoo import http

# class AdvertisingProductMatrix(http.Controller):
#     @http.route('/advertising_product_matrix/advertising_product_matrix/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/advertising_product_matrix/advertising_product_matrix/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('advertising_product_matrix.listing', {
#             'root': '/advertising_product_matrix/advertising_product_matrix',
#             'objects': http.request.env['advertising_product_matrix.advertising_product_matrix'].search([]),
#         })

#     @http.route('/advertising_product_matrix/advertising_product_matrix/objects/<model("advertising_product_matrix.advertising_product_matrix"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('advertising_product_matrix.object', {
#             'object': obj
#         })