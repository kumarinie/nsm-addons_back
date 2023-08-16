# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2015 Odoo Experts
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from odoo import api, fields, models, _

import base64
from io import StringIO
from PyPDF2 import PdfFileReader, PdfFileWriter

class InvoicMergePdf(models.TransientModel):
    _name = 'supplier.invoice.merge.pdf'
    _description = 'Supplier Invoice Merge PDF'

    @api.model
    def _get_file_data(self):
        context = self._context

        invoice_ids = context.get('active_ids',[])
        if not invoice_ids:
            return False

        final_pdf = []
        att_pool = self.env['ir.attachment']
        output = PdfFileWriter()

        for invoice in self.env['account.invoice'].browse(invoice_ids):
            flg = False
            attachments = att_pool.search([('res_model', '=', 'account.invoice'),
                                       ('res_id', '=', invoice.id)])

            for att_data in attachments:
                if 'PDF' not in att_data.mimetype.upper() :
                    continue
                if att_data.datas_fname and att_data.datas and att_data.datas_fname.split(".")[-1].upper() == "PDF":
                    data = base64.decodestring(att_data.datas)
                    buffer_file = StringIO.StringIO(data)
                    input_attachment = PdfFileReader(buffer_file)
                    flg = True
                    for page in range(input_attachment.getNumPages()):
                        output.addPage(input_attachment.getPage(page))

            if not flg:
                result = self.env['report'].get_pdf([invoice.id], "nsm_account.report_blank_invoice")

                buffer_file = StringIO.StringIO(result)
                input_report = PdfFileReader(buffer_file)
                for page in range(input_report.getNumPages()):
                    output.addPage(input_report.getPage(page))

        outputStream = StringIO.StringIO()
        output.write(outputStream)
        res = outputStream.getvalue().encode('base64')
        outputStream.close()

        return res


    file_data = fields.Binary('Merged PDF', default=_get_file_data)
    file_name = fields.Char('File Name', default='Invoice Merged Attachments.pdf')




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
