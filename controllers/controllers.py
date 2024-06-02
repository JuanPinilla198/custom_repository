# -*- coding: utf-8 -*-
# from odoo import http


# class CustomRepository(http.Controller):
#     @http.route('/custom_repository/custom_repository', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_repository/custom_repository/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_repository.listing', {
#             'root': '/custom_repository/custom_repository',
#             'objects': http.request.env['custom_repository.custom_repository'].search([]),
#         })

#     @http.route('/custom_repository/custom_repository/objects/<model("custom_repository.custom_repository"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_repository.object', {
#             'object': obj
#         })

