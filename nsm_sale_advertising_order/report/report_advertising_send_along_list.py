# -*- coding: utf-8 -*-
# from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo import api, fields, models, _
import datetime
from odoo.exceptions import UserError
from odoo.addons.report_xlsx_helper.report.report_xlsx_format import (
    FORMATS,
    XLS_HEADERS,
)


class NSMAdvertisingSendAlongListReport(models.AbstractModel):
    _name = "report.nsm.advertising_send_along_list_report_xlsx"
    _description = "NSMDeliveryListReport XLSL Report"
    _inherit = "report.report_xlsx.abstract"


    def generate_xlsx_report(self, workbook, data, orderLines):

        def _prepare_data(orderLine):
            records = []
            records.append(orderLine.order_id.name)
            records.append(orderLine.order_partner_id.name)
            records.append(orderLine.product_id.name)
            records.append(orderLine.product_uom_qty)
            records.append(orderLine.adv_issue.name)
            records.append(orderLine.issue_date)
            records.append(orderLine.adv_issue_parent.name)
            return records

        def _form_data(orderLines):
            row_datas = []
            for orderLine in orderLines.filtered('send_with_advertising_issue'):
                row_datas.append(_prepare_data(orderLine))
            return row_datas

        header = ['Order Name', 'Order Partner', 'Product', 'Quantity', 'Issue Name', 'Issue Date', 'Parent Issue']

        row_datas = _form_data(orderLines)

        if row_datas:
            bold_format = workbook.add_format({'bold': True})
            report_name = 'ASAL_{date:%Y-%m-%d %H:%M:%S}'.format(date=datetime.datetime.now())
            sheet = workbook.add_worksheet(report_name[:31])
            for i, title in enumerate(header):
                sheet.write(0, i, title, bold_format)
            for row_index, row in enumerate(row_datas):
                for cell_index, cell_value in enumerate(row):
                    sheet.write(row_index + 1, cell_index, cell_value)
            workbook.close()
        else:
            raise UserError(_('No record found to print!'))



# NSMAdvertisingSendAlongListReport('report.report_advertising_send_along_list.xlsx', 'sale.order.line')