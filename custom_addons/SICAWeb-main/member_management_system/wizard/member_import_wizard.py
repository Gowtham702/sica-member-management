# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import io

try:
    import openpyxl
except ImportError:
    openpyxl = None


class MemberImportWizard(models.TransientModel):
    _name = 'member.import.wizard'
    _description = 'Member Import Wizard'

    excel_file      = fields.Binary(string='Excel File', required=True)
    file_name       = fields.Char(string='File Name')
    total_records   = fields.Integer(string='Total Records', readonly=True)
    updated_count   = fields.Integer(string='Updated', readonly=True)
    not_found_count = fields.Integer(string='Not Found', readonly=True)
    error_count     = fields.Integer(string='Errors', readonly=True)
    result_message  = fields.Text(string='Result', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done',  'Done'),
    ], default='draft')

    def action_import(self):
        self.ensure_one()

        if not openpyxl:
            raise UserError(_('openpyxl is not installed.'))

        if not self.excel_file:
            raise UserError(_('Please upload an Excel file.'))

        file_data = base64.b64decode(self.excel_file)
        wb = openpyxl.load_workbook(io.BytesIO(file_data), read_only=True)
        ws = wb.active

        updated   = []
        not_found = []
        errors    = []
        skipped   = 0

        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i == 0:
                continue
            if not row or len(row) < 2:
                skipped += 1
                continue

            membership_no = str(row[0]).strip() if row[0] else ''
            paid_till     = str(row[1]).strip() if row[1] else ''

            if not membership_no or membership_no == 'None':
                skipped += 1
                continue
            if not paid_till or paid_till == 'None':
                skipped += 1
                continue

            try:
                member = self.env['res.member'].search(
                    [('membership_no', '=', membership_no)], limit=1
                )
                if not member:
                    not_found.append(membership_no)
                    continue

                member.write({'paid_till': str(int(float(paid_till)))})
                updated.append(membership_no)

            except Exception as e:
                errors.append(f'{membership_no}: {str(e)}')

        wb.close()

        result  = f'Total Updated  : {len(updated)}\n'
        result += f'Not Found      : {len(not_found)}\n'
        result += f'Errors         : {len(errors)}\n'
        result += f'Skipped        : {skipped}\n'

        if not_found:
            result += f'\nNot found:\n' + '\n'.join(not_found[:20])
        if errors:
            result += f'\nErrors:\n' + '\n'.join(errors[:10])

        self.write({
            'total_records'  : len(updated) + len(not_found) + len(errors),
            'updated_count'  : len(updated),
            'not_found_count': len(not_found),
            'error_count'    : len(errors),
            'result_message' : result,
            'state'          : 'done',
        })

        # Stay on same page — no popup
        return {
            'type'     : 'ir.actions.act_window',
            'res_model': 'member.import.wizard',
            'res_id'   : self.id,
            'view_mode': 'form',
            'target'   : 'current',
        }

    def action_reset(self):
        self.write({
            'excel_file'    : False,
            'file_name'     : False,
            'state'         : 'draft',
            'result_message': False,
        })
        return {
            'type'     : 'ir.actions.act_window',
            'res_model': 'member.import.wizard',
            'res_id'   : self.id,
            'view_mode': 'form',
            'target'   : 'current',
        }