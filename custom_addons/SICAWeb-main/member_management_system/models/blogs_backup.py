from odoo import api, models, fields
import logging
import firebase_admin
from firebase_admin import messaging
from firebase_admin._messaging_utils import UnregisteredError

_logger = logging.getLogger(__name__)


class SicaBlog(models.Model):
    _name = 'sica.blog'
    _description = 'Sica Blog'
    _rec_name = 'title'

    title = fields.Char()
    date = fields.Date()
    views = fields.Integer()
    sequence = fields.Integer()
    description = fields.Html()
    image = fields.Binary()
    image_note = fields.Char(default='16:6 or 1:1')

    @api.model
    def create(self, vals):
        title = str(vals.get('title') or 'Blog added')
        body = title
        source = 'SICA Blog'
        self.update_notification(title, body, source)
        return super(SicaBlog, self).create(vals)

    def update_notification(self, title, body, source):
        _logger = logging.getLogger(__name__)
        
        send = self.env['push.notification.log.history'].sudo().create({
            'source': source,   
            'date_send': fields.Datetime.now(),
        })

        send_id = f"https://new.thesica.in/homepage/newstabbarwidget/blogs?title={title}"
        
        members = self.env['res.member'].sudo().search([('token', '!=', False)])
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
                _logger.info(f"Push sent to {member.name} ({member.membership_no}): {response}")
            except UnregisteredError:
                _logger.warning(f"Unregistered FCM token. Clearing token for member {member.name}")
                member.token = False
            except Exception as e:
                _logger.error(f"Push failed for {member.name} ({member.membership_no}): {str(e)}")

class SicaFeatures(models.Model):
    _name = 'sica.features'
    _description = 'Sica Features'
    _rec_name = 'title'

    title = fields.Char()
    date = fields.Date()
    views = fields.Integer()
    sequence = fields.Integer()
    description = fields.Html()
    attachments_ids = fields.Many2many('ir.attachment', public=True)
    image_note = fields.Char(default='16:6 or 1:1')