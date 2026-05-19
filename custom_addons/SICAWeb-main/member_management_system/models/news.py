from odoo import api,models,fields
import logging
from firebase_admin import messaging
from firebase_admin._messaging_utils import UnregisteredError

_logger = logging.getLogger(__name__)

class SicaNews(models.Model):
    _name = 'sica.news'
    _description = 'Sica News'
    _rec_name = 'title'
    _order = 'sequence desc'

    def default_get(self, fields):
        res = super(SicaNews, self).default_get(fields)
        if 'sequence' in fields:
            last_seq = self.env['sica.news'].search([], order="sequence desc", limit=1).sequence
            res['sequence'] = last_seq + 1 if last_seq else 1
        return res

    title = fields.Char()
    date = fields.Date()
    sequence = fields.Integer()
    views = fields.Integer()
    description = fields.Html()
    image = fields.Binary()
    image_note = fields.Char(default='16:6 or 1:1')

    @api.model
    def create(self, vals):
        if vals.get('title'):
            title = str(vals.get('title')) or ''
            body = str(vals.get('title')) or ''
        else:
            title = 'New Sica News created'
            body = 'New Sica News created'
        title = 'News added'
        source = 'SICA News'
        self.update_notification(title, body, source)
        return super(SicaNews, self).create(vals)

    def update_notification(self, title, body, source):
        
        _logger.info(f"Sending push notification for News: {title}")

        self.env['push.notification.log.history'].sudo().create({
            'source': source,
            'date_send': fields.Datetime.now(),
        })

        send_id = f"https://new.thesica.in/homepage/newstabbarwidget/news?title={title}"

        members = self.env['res.member'].sudo().search([('token', '!=', False)])

        for member in members:
            print("member.token")
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
                _logger.warning(f"Unregistered token: {member.name}")
                member.token = False
            except Exception as e:
                _logger.error(f"Push failed for {member.name}: {str(e)}")