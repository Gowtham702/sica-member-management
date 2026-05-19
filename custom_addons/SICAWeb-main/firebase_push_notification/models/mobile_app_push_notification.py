# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
#    Odoo                                                                    #
#    Copyright (C) 2023-2024 Feddad Imad (feddad.imad@gmail.com)             #
#                                                                            #
##############################################################################


from odoo import models, fields, api, _
import requests

from odoo.exceptions import UserError, ValidationError

import firebase_admin
from firebase_admin import credentials, messaging
import os
import logging
_logger = logging.getLogger(__name__)



class MobileAppPushNotification(models.Model):
    _name = 'mobile.app.push.notification'
    _description = 'Push Notification'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _order = 'id desc'

    @api.onchange('send_notification_to')
    def _onchange_send_notification_to(self):
        if self.send_notification_to == 'to_all':
            self.member_ids = False


    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('done', 'Sent'),
        ('Planned', 'Planned'),
        ('cancel', 'Cancel'),
        ('error', 'Error'),
    ]
    # cred = credentials.Certificate("/opt/odoo15/SICAWeb/firebase_push_notification/data/serviceAccountKey.json")

    # firebase_admin.initialize_app(cred)

    name = fields.Char('Title', tracking=True)
    body = fields.Text('Message', tracking=True)
    send_notification_to = fields.Selection([('to_all','All Members'),('to_specefic','To a Member')], string='Send To', default='to_all', tracking=True)

    # log_history = fields.One2many('push.notification.log.history', 'notification_id', 'History' )
    log_history = fields.One2many('push.notification.log.partner','notification_id', string="Logs")

    member_ids = fields.Many2many('res.member', string="Member")
    image = fields.Binary('Image', attachment=True)
    image_url = fields.Char("Image URL (Auto Generated)")
    links = fields.Char("Links")
    image_link = fields.Char("Image Link")
    state = fields.Selection(STATE_SELECTION, 'Status', readonly=True, default='draft', tracking=True)

    def _make_image_public(self):
        if not self.image:
            return

        attachment = self.env['ir.attachment'].sudo().search([
            ('res_model', '=', 'mobile.app.push.notification'),
            ('res_id', '=', self.id),
            ('res_field', '=', 'image')
        ], limit=1)

        if attachment and not attachment.public:
            attachment.sudo().write({'public': True})
            self.image_url = f"/web/image/{attachment.id}"


    def send_notification(self):
        self.ensure_one()
        self._make_image_public()

        # Fetch target members
        if self.send_notification_to == 'to_all':
            members = self.env['res.member'].search([('token', '!=', False)])
            if not members:
                raise UserError(_("No members found with Firebase tokens."))
        else:
            if not self.member_ids:
                raise UserError(_("Please select at least one member."))

            members = self.member_ids.filtered(lambda m: m.token)
            if not members:
                raise UserError(_("No selected member has a valid Firebase token."))

        # Generate image URL
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url.image')
        image_url = base_url + self.image_url

        success_count = 0
        fail_count = 0

        for member in members:
            try:
                # Firebase message with image
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=self.name or '',
                        body=self.body or '',
                        image=image_url if image_url else None
                    ),
                    data={
                        "image": image_url or "",
                        "links": self.links or "",
                        "click_action": "FLUTTER_NOTIFICATION_CLICK"
                    },
                    token=member.token,
                )

                response = messaging.send(message)
                _logger.info("Notification sent to %s: %s", member.name, response)

                # Log success
                self.env['push.notification.log.partner'].sudo().create({
                    'notification_id': self.id,
                    'member_id': member.id,
                    'date_send': fields.Datetime.now(),
                    'notification_state': 'success',
                })

                success_count += 1

            except Exception as e:
                _logger.error("Error sending to %s: %s", member.name, e)

                # Log failure
                self.env['push.notification.log.partner'].sudo().create({
                    'notification_id': self.id,
                    'member_id': member.id,
                    'date_send': fields.Datetime.now(),
                    'notification_state': 'failed',
                })

                fail_count += 1

        # Update state
        if success_count > 0 and fail_count == 0:
            self.state = 'done'
        elif success_count > 0:
            self.state = 'error'
        else:
            self.state = 'error'

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Notification Summary"),
                'message': _("%s sent, %s failed.") % (success_count, fail_count),
                'type': 'success' if fail_count == 0 else 'warning',
            }
        }


class PushNotificationLogHistory(models.Model):
    _name = 'push.notification.log.history'
    _description = 'Push Notification'


    notification_id = fields.Many2one('mobile.app.push.notification')
    member_id = fields.Many2one('res.member', string="Member")
    source = fields.Char(string="Source")
    date_send = fields.Datetime("Send Date")
    notification_state = fields.Selection([('success','Succès'),('failed','Échoué')], string="State")

    




