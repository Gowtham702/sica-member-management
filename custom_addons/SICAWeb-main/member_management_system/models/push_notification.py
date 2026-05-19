# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import requests

from odoo.exceptions import UserError, ValidationError

import firebase_admin
from firebase_admin import credentials,messaging

# Load your service account key JSON file
# cred = credentials.Certificate("/opt/odoo15/SICAWeb/firebase_push_notification/data/serviceAccountKey.json")

# Initialize the app with the service account
# firebase_admin.initialize_app(cred)
import os
import logging
_logger = logging.getLogger(__name__)

class PushNotificationLogHistory(models.Model):
    _name = 'push.notification.log.history'
    _description = 'Push Notification'

    member_id = fields.Many2many('res.member', string="Member")
    source = fields.Char(string="Source")
    date_send = fields.Datetime("Send Date")
    notification_state = fields.Selection([('success','Success'),('failed','Failed')], string="State")

    def send_notification(self, title, body, source, send_id):
        device_ids = self.env['res.member'].sudo().search([]).filtered(lambda x: x.token)
        for tok in device_ids:
            message = messaging.Message(
                data={
                    "path": send_id or '',
                },
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                token=tok.token,
            )
            # Send the message
            response = messaging.send(message)
            if response:
                self.write({
                    'member_id': device_ids,
                    'date_send': fields.Datetime.now(),
                    'notification_state': 'success',
                })
                self.write({'notification_state': 'success'})
            print("Successfully sent message:", response)
