from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import csv
import xlrd
from io import StringIO, BytesIO


class ProductVendorImportWizard(models.TransientModel):
    _name = 'product.vendor.import.wizard'
    _description = 'Import Product Vendor Line Wizard'

    file = fields.Binary("Upload File", required=False)
    file_name = fields.Char("File Name")

    # -----------------------------------------------------------
    # TEMPLATE DOWNLOAD
    # -----------------------------------------------------------
    def action_download_template(self):
        template = (
            "Vendor Name,Category,Product Name,Sequence,Description,Quantity,Image Link\n"
            "Electronics Vendors,Electrical Parts,Voltage Regulator,1,Regulator for motors,100,https://example.com/image1.jpg\n"
            "Electronics Vendors,Electrical Parts,Copper Wire,2,High quality copper wire,300,https://example.com/image2.jpg\n"
        )

        self.write({
            'file': base64.b64encode(template.encode("utf-8")),
            'file_name': "ProductVendorTemplate.csv"
        })

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{self._name}/{self.id}/file/ProductVendorTemplate.csv?download=true",
            "target": "self",
        }

    # -----------------------------------------------------------
    # IMPORT ENTRY
    # -----------------------------------------------------------
    def action_import_file(self):
        if not self.file:
            raise UserError("Please upload a CSV or Excel file.")

        file_data = base64.b64decode(self.file)

        # Detect File Type
        if self.file_name.lower().endswith(('.xls', '.xlsx')):
            return self._import_excel(file_data)
        else:
            return self._import_csv(file_data.decode('utf-8'))

    # -----------------------------------------------------------
    # CSV IMPORT
    # -----------------------------------------------------------
    def _import_csv(self, data):

        csv_data = csv.DictReader(StringIO(data))

        lines = list(csv_data)

        if not lines:
            raise UserError("Uploaded CSV file is empty. Please fill the template before importing.")

        for row in lines:
            self._create_vendor_line(row)

        return self._notify("Excel import completed successfully!")

    # -----------------------------------------------------------
    # EXCEL IMPORT
    # -----------------------------------------------------------
    def _import_excel(self, file_data):

        wb = xlrd.open_workbook(file_contents=file_data)
        sheet = wb.sheet_by_index(0)

        headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
        rows = []

        for row in range(1, sheet.nrows):
            row_dict = {headers[col]: sheet.cell_value(row, col) for col in range(sheet.ncols)}
            rows.append(row_dict)

        if not rows:
            raise UserError("Uploaded Excel file is empty. Please fill the template before importing.")

        for row in rows:
            self._create_vendor_line(row)

        return self._notify("Excel import completed successfully!")

    # -----------------------------------------------------------
    # CENTRAL RECORD CREATION
    # -----------------------------------------------------------
    def _create_vendor_line(self, vals):

        # Normalize Column Keys (avoid mistakes)
        vendor_name = (vals.get('Vendor Name') or '').strip()
        category_name = (vals.get('Category') or '').strip()
        product_name = (vals.get('Product Name') or '').strip()
        image_link = (vals.get('Image Link') or '').strip()

        if not vendor_name:
            raise UserError("Vendor Name missing in one of the rows.")

        # --------------------------------------------
        # FIND SUB CATEGORY (Vendor)
        # --------------------------------------------
        sp_category = self.env['spd.sub.category'].search([
            ('name', 'ilike', vendor_name)
        ], limit=1)

        if not sp_category:
            raise UserError(f"Vendor/Sub Category not found: {vendor_name}")

        # --------------------------------------------
        # FIND OR CREATE CATEGORY
        # --------------------------------------------
        category = False
        if category_name:
            category = self.env['spd.category'].search([
                ('name', 'ilike', category_name)
            ], limit=1)

            if not category:
                category = self.env['spd.category'].create({'name': category_name})

        # --------------------------------------------
        # CREATE PRODUCT VENDOR LINE
        # --------------------------------------------
        print('vals.get', vals)
        self.env['product.vendor.line'].create({
            'sp_category_id': sp_category.id,
            'category_id': category.id if category else False,
            'name': product_name,
            'sequence': int(vals.get('Sequence') or 0),
            'description': vals.get('Description'),
            'quantity': int(vals.get('Quantity') or 0),
            'image_link': image_link,
        })

    # -----------------------------------------------------------
    # NOTIFICATION
    # -----------------------------------------------------------
    def _notify(self, message):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Import Completed',
                'message': "Excel Imported Successfully!",
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'}
            }
        }
