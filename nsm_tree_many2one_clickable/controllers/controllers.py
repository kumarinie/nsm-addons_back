# -*- coding: utf-8 -*-
from odoo import http

# class NsmTreeMany2oneClickable(http.Controller):
#     @http.route('/nsm_tree_many2one_clickable/nsm_tree_many2one_clickable/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/nsm_tree_many2one_clickable/nsm_tree_many2one_clickable/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('nsm_tree_many2one_clickable.listing', {
#             'root': '/nsm_tree_many2one_clickable/nsm_tree_many2one_clickable',
#             'objects': http.request.env['nsm_tree_many2one_clickable.nsm_tree_many2one_clickable'].search([]),
#         })

#     @http.route('/nsm_tree_many2one_clickable/nsm_tree_many2one_clickable/objects/<model("nsm_tree_many2one_clickable.nsm_tree_many2one_clickable"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nsm_tree_many2one_clickable.object', {
#             'object': obj
#         })