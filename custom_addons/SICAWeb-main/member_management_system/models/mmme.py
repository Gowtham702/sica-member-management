from odoo import api,models,fields
import logging
from firebase_admin import messaging
from firebase_admin._messaging_utils import UnregisteredError

_logger = logging.getLogger(__name__)

class MyMovieMyExperience(models.Model):
    _name = 'mymovie.myexperience'
    _description = 'My Movie My Experience'
    _rec_name = 'title'

    def default_get(self, fields):
        res = super(MyMovieMyExperience, self).default_get(fields)
        if 'sequence' in fields:
            last_seq = self.env['mymovie.myexperience'].search([], order="sequence desc", limit=1).sequence
            res['sequence'] = last_seq + 1 if last_seq else 1
        return res

    title = fields.Char()
    date = fields.Date()
    views = fields.Integer()
    sequence = fields.Integer()
    description = fields.Html()
    image = fields.Binary()
    image_note = fields.Char(default='16:6 or 1:1')
    state = fields.Selection([
        ("draft", "Draft"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ], default="draft", copy=False, string="Status")

    # def action_approve(self):
    #     title = str(vals.get('title') or 'New Experience')
    #     body = title
    #     source = 'SICA Experience'
    #     self.update_notification(title, body, source)
    #     self.write({
    #         'state': 'approved',
    #     })

    def action_approve(self):
        for record in self:
            title = record.title or 'New Experience'
            body = title
            source = 'SICA Experience'
            record.update_notification(title, body, source)
            record.write({
                'state': 'approved',
            })

    def action_reject(self):
        self.write({
            'state': 'rejected',
        })

    
    @api.model
    def create(self, vals):
        title = str(vals.get('title') or 'New Experience')
        body = title
        source = 'SICA Experience'
        # self.update_notification(title, body, source)
        return super(MyMovieMyExperience, self).create(vals)

    def update_notification(self, title, body, source):
        _logger.info(f"Sending push notification for Experience: {title}")

        # Log the push
        self.env['push.notification.log.history'].sudo().create({
            'source': source,
            'date_send': fields.Datetime.now(),
        })

        # Create the URL (you can customize this)
        send_id = f"https://new.thesica.in/homepage/mymovieexperience/details/:{title}"

        # Send to members with valid FCM tokens
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
                _logger.warning(f"Unregistered token: {member.name}")
                member.token = False
            except Exception as e:
                _logger.error(f"Push failed for {member.name}: {str(e)}")