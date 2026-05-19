# -*- coding: utf-8 -*-
import os
import shutil
import tempfile

from odoo import models, fields, api
from odoo.exceptions import UserError

try:
   import qrcode
except ImportError:
   qrcode = None
try:
   import base64
except ImportError:
   base64 = None
from io import BytesIO
from datetime import date, datetime, timedelta


class SicaSupport(models.Model):
    _name = "sica.support"
    _description = "SICA Help and Support"
    _order = "id desc"

    support_no = fields.Char(default="/", copy=False, readonly=True, tracking=True, string="Support No.")
    image_1920 = fields.Binary(string="Image")
    member_id = fields.Many2one('res.member', string="Member ID")
    member_name = fields.Char(string="Member Name")
    date = fields.Date(string="Date")
    type_of_issue = fields.Char(string="Type of Issues")
    details = fields.Char(string="Details")
    app_version = fields.Char(string="App Version")
    additional_notes = fields.Html(string="Additional Notes")

    @api.model
    def create(self, vals):
        if vals.get("support_no", "/") == "/":
            vals["support_no"] = self.env["ir.sequence"].next_by_code("sica.support")
        return super(SicaSupport, self).create(vals)