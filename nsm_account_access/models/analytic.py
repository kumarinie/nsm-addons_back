# -*- coding: utf-8 -*-

from lxml import etree
from odoo import models, fields, api, _
from odoo.osv.orm import setup_modifiers
from odoo import SUPERUSER_ID

class AnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        result = super(AnalyticLine, self).fields_view_get(
            view_id, view_type, toolbar, submenu)

        Is_redactie_grp = self.env.user.has_group('nsm_account_access.account_extra_access_redactie')
        if not SUPERUSER_ID == self._uid and Is_redactie_grp and view_type in ['tree','form']:
            arch = etree.fromstring(result['arch'])
            for field in arch.xpath('//tree'):
                field.attrib['create'] = 'false'
                field.attrib['edit'] = 'false'
            for field in arch.xpath('//form'):
                field.attrib['create'] = 'false'
                field.attrib['edit'] = 'false'
            result['arch'] = etree.tostring(arch)

            if view_type == 'form':
                doc = etree.XML(result['arch'])
                acc_nodes = doc.xpath("//field[@name='account_id']")
                if acc_nodes:
                    acc_nodes[0].set('options', '{"no_create": True, "no_create_edit": True, "no_open": True}')
                    setup_modifiers(
                        acc_nodes[0], result['fields']['account_id'])
                    result['arch'] = etree.tostring(doc)
                gen_nodes = doc.xpath("//field[@name='general_account_id']")
                if gen_nodes:
                    gen_nodes[0].set('options', '{"no_create": True, "no_create_edit": True, "no_open": True}')
                    setup_modifiers(
                        gen_nodes[0], result['fields']['general_account_id'])
                    result['arch'] = etree.tostring(doc)
                part_nodes = doc.xpath("//field[@name='partner_id']")
                if part_nodes:
                    part_nodes[0].set('options', '{"no_create": True, "no_create_edit": True, "no_open": True}')
                    setup_modifiers(
                        part_nodes[0], result['fields']['partner_id'])
                    result['arch'] = etree.tostring(doc)
                move_nodes = doc.xpath("//field[@name='move_id']")
                if move_nodes:
                    move_nodes[0].set('options', '{"no_create": True, "no_create_edit": True, "no_open": True}')
                    setup_modifiers(
                        move_nodes[0], result['fields']['move_id'])
                    result['arch'] = etree.tostring(doc)
        return result
