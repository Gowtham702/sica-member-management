from odoo import api,models,fields
import firebase_admin
from firebase_admin import messaging
from firebase_admin._messaging_utils import UnregisteredError
import logging

_logger = logging.getLogger(__name__)

class TechTalk(models.Model):
    _name = 'tech.talk'
    _description = 'Tech Talk'
    _rec_name = 'title'

    title = fields.Char()
    date = fields.Date()
    sequence = fields.Integer()
    views = fields.Integer()
    link = fields.Char()
    image = fields.Binary()
    image_note = fields.Char(default='16:6 or 1:1')

    @api.model
    def create(self, vals):
        if vals.get('title'):
            title = str(vals.get('title')) or ''
            body = str(vals.get('title')) or ''
        else:
            title = 'New Sica Tech Talk created'
            body = 'New Sica Tech Talk created'
        title = 'Tech Talk added'
        source = 'SICA talks'
        # self.update_notification(title, body, source)
        return super(TechTalk, self).create(vals)

    print("tttttttttttttt11111111111111111111111")
    def update_notification(self, title, body, source):
        send = self.env['push.notification.log.history'].sudo().create({
            'source': 'SICA talks',
            'date_send': fields.Datetime.now(),
        })
        send_id = "https://new.thesica.in/homepage/newstabbarwidget/news?title="+title
        members = self.env['res.member'].sudo().search([('token', '!=', False)])
        _logger.info(f"Talks Push sent to {member.name} ({member.membership_no}): {response}")

        for member in members:
            try:
                message = messaging.Message(
                    token=member.token,
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    data={"url": send_id}
                )
                response = messaging.send(message)
                _logger.info(f"Talks Push sent to {member.name} ({member.membership_no}): {response}")
            except UnregisteredError:
                _logger.warning(f"Unregistered token: {member.name}")
                member.token = False
            except Exception as e:
                _logger.error(f"Failed to send to {member.name}: {str(e)}")