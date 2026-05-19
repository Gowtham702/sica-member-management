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

import time,pytz
from datetime import datetime,timedelta,timezone,date
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)


class ResMember(models.Model):
    _inherit = 'res.member'

    view_sica_discussion_count = fields.Integer(compute="get_discussion_count", string="Discussion Comment")
    view_sica_discussion_count_form = fields.Integer(compute="get_discussion_form_count", string="Discussion Form")

    def get_discussion_count(self):
        for member in self:
            member.view_sica_discussion_count = self.env["discussion.comment"].search_count([("member_id", "=", member.id)])

    def get_discussion_form_count(self):
        for member in self:
            member.view_sica_discussion_count_form = self.env["discussion.forum"].search_count([("member_id", "=", member.id)])


    def view_sica_discussion(self):
        self.ensure_one()
        result = {
            "type": "ir.actions.act_window",
            "res_model": "discussion.comment",
            "domain": [("member_id", "=", self.id)],
            "context": {"create": False, "edit": False, "delete": False},
            "name": "Discussion Comment",
            'view_mode': 'tree,form',
        }
        return result

    def view_sica_discussion_form(self):
        self.ensure_one()
        result = {
            "type": "ir.actions.act_window",
            "res_model": "discussion.forum",
            "domain": [("member_id", "=", self.id)],
            "context": {"create": False, "edit": False, "delete": False},
            "name": "Discussion Forum",
            'view_mode': 'tree,form',
        }
        return result

    @api.model
    def get_tiles_data(self):

        today = fields.Date.today()
        tomorrow_date = today + relativedelta(days=1)

        today_list = []
        tomorrow_list = []

        today_birthday_member = self.env['res.member'].sudo().search([('dob', 'like', today.strftime('-%m-%d'))])
        tomorrow_birthday_member = self.env['res.member'].sudo().search([('dob', 'like', tomorrow_date.strftime('-%m-%d'))])

        for rec in today_birthday_member:
            today_list.append(rec.name+" - "+str(rec.membership_no))
        for rec2 in tomorrow_birthday_member:
            tomorrow_list.append(rec2.name+" - "+str(rec2.membership_no))


        return {
            'today_birthday': today_list,
            'tomorrow_birthday': tomorrow_list,
        }

class PrivacyPolicy(models.Model):
    _name = 'privacy.policy'
    _description = 'Privacy Policy'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    noted = fields.Html(string='Website Privacy Policy', translate=True, help="Write the content for website policy.")
    is_publish = fields.Boolean(string='Is Publish?')
