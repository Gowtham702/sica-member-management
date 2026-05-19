from odoo import models,fields,api,_
import json
import base64
import urllib
import logging
import requests,http

from odoo.http import request
import firebase_admin
from firebase_admin import messaging
from firebase_admin._messaging_utils import UnregisteredError

_logger = logging.getLogger(__name__)

class EventCategory(models.Model):
    _name = 'event.category'
    _description = 'Event Category'

    name = fields.Char()


class ShootingEvent(models.Model):
    _name = 'shooting.event'
    _description = 'Shooting Events'
    _rec_name = 'title'

    def default_get(self, fields):
        res = super(ShootingEvent, self).default_get(fields)
        if 'sequence' in fields:
            last_seq = self.env['shooting.event'].search([], order="sequence desc", limit=1).sequence
            res['sequence'] = last_seq + 1 if last_seq else 1
        return res

    reference = fields.Char(string='Reference', readonly=True)
    title = fields.Char()
    amount = fields.Float()
    description = fields.Html()
    sequence = fields.Integer()
    image = fields.Binary()
    coach_name = fields.Char()
    start_date = fields.Date()
    end_date = fields.Date()
    media_ids = fields.One2many('shooting.event.media', 'event_id', string='Media Files')
    category_id = fields.Many2one('event.category')
    booking_status_ids = fields.One2many('event.payment', 'event_id')
    is_completed = fields.Boolean()
    event_link = fields.Char()
    venue = fields.Text()
    time = fields.Char()
    map = fields.Char()
    program_presenters = fields.Char()
    presised_by = fields.Char()
    chief_guest = fields.Char()
    note = fields.Text()
    attachments_ids = fields.Many2many('ir.attachment', public=True)
    complete_event_ids = fields.One2many('event.complete.image', 'event_id')
    images_note = fields.Char(default='Square (1:1) or 16:4 or 16:6')
    event_links_ids = fields.One2many('event.links', 'event_id')

    def action_completed_event(self):
        for rec in self:
            rec.is_completed = True

    @api.model
    def create(self, vals):
        if not vals.get('reference') or vals['reference'] == _('/'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('shooting.event') or _('/')
        if vals.get('title'):
            title = str(vals.get('title')) or ''
            body = str(vals.get('title')) or ''
            category_id = str(vals.get('category_id')) or ''
        else:
            title = 'New Event created'
            body = 'Event created'
            category_id = ''
        title = 'Event Added'
        source = 'SICA Event'
        self.update_notification(title, body, category_id, source)
        return super(ShootingEvent, self).create(vals)

    # def update_notification(self, title, body, category_id, source):
    #     send = self.env['push.notification.log.history'].sudo().create({
    #         'source': 'SICA Event',
    #         'date_send': fields.Datetime.now(),
    #     })
    #     send_id = "https://new.thesica.in/homepage/eventtabbar/eventdetails/:"+title+"?category_id="+category_id
    #     if send:
    #         send.send_notification(title, body, source, send_id)

    print("TE1111111111111111111111111111111111111111111111111111111111")
    def update_notification(self, title, body, category_id, source):
        _logger.info(f"Sending event push: {title} - {category_id}")
        
        # Log push event
        self.env['push.notification.log.history'].sudo().create({
            'source': source,
            'date_send': fields.Datetime.now(),
        })

        # Build event link
        send_id = f"https://new.thesica.in/homepage/eventtabbar/eventdetails/:{title}?category_id={category_id}"

        # Get members with FCM tokens
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
                _logger.info(f"Event Push sent to {member.name} ({member.membership_no}): {response}")
            except UnregisteredError:
                _logger.warning(f"Unregistered token: {member.name}")
                member.token = False
            except Exception as e:
                _logger.error(f"Failed to send to {member.name}: {str(e)}")


class ShootingPaymentStatus(models.Model):
    _name = 'event.payment'
    _description = 'Events Payment'

    event_id = fields.Many2one('shooting.event')
    member_id = fields.Many2one('res.member')
    payment_status = fields.Selection([
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
        ('Not Paid', 'Not Paid'),
        ('refund', 'Refund')
    ])
    booking_status = fields.Selection([
        ('Booked', 'Booked'),
        ('Cancelled', 'Cancelled')
    ])
    reason = fields.Char()

class CompleteEventDetails(models.Model):
    _name = 'event.complete.image'
    _description = 'Events Complete Details'

    event_id = fields.Many2one('shooting.event')
    attachments_ids = fields.Many2many('ir.attachment', public=True)
    image = fields.Binary(string="Image")
    event_link = fields.Char('Event Link')



class ShootingEventMedia(models.Model):
    _name = 'shooting.event.media'
    _description = 'Shooting Event Media'
    _order = 'sequence'

    event_id = fields.Many2one('shooting.event', string='Shooting Event', ondelete='cascade')
    file = fields.Binary(string="Media File", required=True, attachment=True)
    file_name = fields.Char(string="Filename")
    media_type = fields.Selection(
        [('image', 'Image'), ('video', 'Video')],
        string="Media Type",
        compute='_compute_media_type',
        store=True,
        default='image'
    )
    sequence = fields.Integer(string="Sequence", default=10)

    @api.depends('file_name')
    def _compute_media_type(self):
        for record in self:
            filename = record.file_name or ''
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                record.media_type = 'image'
            elif filename.lower().endswith(('.mp4', '.mov', '.avi')):
                record.media_type = 'video'
            else:
                record.media_type = 'image'  # Default fallback


class EventLinks(models.Model):
    _name = 'event.links'
    _description = 'Event Links'

    event_id = fields.Many2one('shooting.event')
    link = fields.Char()
