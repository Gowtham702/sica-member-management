# -*- coding: utf-8 -*-
import io
import base64
import xlsxwriter
from odoo import models, fields
from datetime import date, datetime


class ProfitLossReport(models.TransientModel):
    _name = "profit.loss.report"
    _description = "Profit & Loss Report"

    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    sica_cbt = fields.Selection([
        ("SICA", "SICA"),
        ("CBT", "CBT"),
    ], string="SICA/CBT")
    file = fields.Binary(string="File")
    filename = fields.Char(string="File Name")

    def download_excel_file(self):
        domain = []
        opening_balance = 0
        filename = "Profit & Loss Report"

        if self.date_from and self.date_to:
            filename += " From %s to %s" % (self.date_from.strftime('%d/%m/%Y'), self.date_to.strftime('%d/%m/%Y'))
        elif self.date_from:
            filename += " From %s" % self.date_from.strftime('%d/%m/%Y')
        elif self.date_to:
            filename += " As of %s" % self.date_to.strftime('%d/%m/%Y')

        if self.date_from:
            domain.append(("transaction_date", ">=", self.date_from))
            self.env.cr.execute("SELECT SUM(cash) FROM profit_loss WHERE transaction_date < '%s'" % self.date_from)
            opening_balance += self.env.cr.fetchone()[0] or 0.0
            self.env.cr.execute("SELECT SUM(bank) FROM profit_loss WHERE transaction_date < '%s'" % self.date_from)
            opening_balance += self.env.cr.fetchone()[0] or 0.0
        if self.date_to:
            domain.append(("transaction_date", "<=", self.date_to))
        if self.sica_cbt:
            domain.append(("sica_cbt", "in", [False, self.sica_cbt]))
            filename += "(Type: %s)" % self.sica_cbt
        filename += ".xlsx"

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'font_size': 15, 'bold': 1})
        bold_right = workbook.add_format({'font_size': 15, 'bold': 1, 'align': 'right'})
        normal_columns = workbook.add_format({'font_size': 15})

        # Width of columns
        worksheet.set_column(0, 0, 20)
        worksheet.set_column(1, 1, 20)
        worksheet.set_column(2, 2, 30)
        worksheet.set_column(3, 3, 20)
        worksheet.set_column(4, 4, 18)
        worksheet.set_column(5, 5, 18)
        worksheet.set_column(6, 6, 20)

        # Header
        row = 0
        worksheet.write(row, 0, "Transaction Type", bold)
        worksheet.write(row, 1, "Transaction Date", bold)
        worksheet.write(row, 2, "Description", bold)
        worksheet.write(row, 3, "Opening Balance", bold_right)
        worksheet.write(row, 4, "Cash", bold_right)
        worksheet.write(row, 5, "Bank", bold_right)
        worksheet.write(row, 6, "Closing Balance", bold_right)

        # Content
        pl_data = self.env["profit.loss"].search_read(domain=domain,
                  fields=["transaction_type", "transaction_date", "description", "cash", "bank"])
        for pl_vals in pl_data:
            row += 1
            worksheet.write(row, 0, pl_vals["transaction_type"], normal_columns)
            worksheet.write(row, 1, pl_vals["transaction_date"].strftime('%d/%m/%Y'), normal_columns)
            worksheet.write(row, 2, pl_vals["description"], normal_columns)
            worksheet.write(row, 3, opening_balance, normal_columns)
            worksheet.write(row, 4, pl_vals["cash"], normal_columns)
            worksheet.write(row, 5, pl_vals["bank"], normal_columns)
            opening_balance += pl_vals["cash"] + pl_vals["bank"]
            worksheet.write(row, 6, opening_balance, normal_columns)


        row += 4
        worksheet.merge_range(row, 0, row, 2, "Summary of Txns done on %s"% date.today().strftime("%d/%m/%Y"), bold)

        row += 1
        worksheet.write(row, 1, "Subscription", bold_right)
        worksheet.write(row, 2, "Other Receipts", bold_right)
        worksheet.write(row, 3, "Cash Deposit", bold_right)
        worksheet.write(row, 4, "Cash Withdrawn", bold_right)
        worksheet.write(row, 5, "Cash Expense", bold_right)
        worksheet.write(row, 6, "Cash In Hand", bold_right)

        row += 1
        worksheet.write(row, 0, "SICA", bold_right)
        worksheet.write(row, 1, 0.0, bold_right)
        worksheet.write(row, 2, 0.0, bold_right)
        worksheet.write(row, 3, 0.0, bold_right)
        worksheet.write(row, 4, 0.0, bold_right)
        worksheet.write(row, 5, 0.0, bold_right)
        worksheet.write(row, 6, 0.0, bold_right)

        row += 1
        worksheet.write(row, 0, "CBT", bold_right)
        worksheet.write(row, 1, 0.0, bold_right)
        worksheet.write(row, 2, 0.0, bold_right)
        worksheet.write(row, 3, 0.0, bold_right)
        worksheet.write(row, 4, 0.0, bold_right)
        worksheet.write(row, 5, 0.0, bold_right)
        worksheet.write(row, 6, 0.0, bold_right)


        workbook.close()
        output.seek(0)
        result = base64.b64encode(output.read())
        self.write({'filename': filename, 'file': result})
        output.close()

        return {
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=profit.loss.report&id=" + str(
                self.id) + "&filename_field=filename&field=file&download=true&name=",
            'target': 'self'
        }


ProfitLossReport()
