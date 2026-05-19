import json
import firebase_admin
from firebase_admin import messaging
from firebase_admin._messaging_utils import UnregisteredError
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
class JobTitle(models.Model):
    _name = 'job.title'
    _description = 'Job Title'

    name = fields.Char()


class MemberJobSeeker(models.Model):
    _name = 'member.job.seeker'
    _inherit = ["mail.thread", "mail.activity.mixin", "format.address.mixin", "avatar.mixin"]

    _description = 'Member Job Seeker'

    name = fields.Char(string='Reference', default='/', readonly=True)
    member_id = fields.Many2one('res.member')
    mobile_number = fields.Char()
    member_name = fields.Char()
    membership_no = fields.Char()
    designation = fields.Char()
    skill_1 = fields.Text()
    skill_2 = fields.Text()
    skill_ids = fields.Many2many('member.skill')
    post_applying = fields.Many2many('job.title')
    post_applying_id = fields.Many2one('job.title')
    post_applying_ids_json = fields.Char(compute='get_post_applying_ids_json')
    start_date = fields.Date()
    till_date = fields.Date()
    available_date = fields.Date()
    experience = fields.Char()
    portifolio_link = fields.Char()
    portifolio_link_2 = fields.Char()
    note = fields.Text()
    document = fields.Char()
    document_binary = fields.Binary()
    profile_pic = fields.Binary()
    medium = fields.Many2many('member.medium')
    medium_id = fields.Many2one('member.medium')
    medium_ids_json = fields.Char(compute='get_medium_ids_json')
    state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], default='active')
    active = fields.Boolean(default='True')
    # description = fields.Char()
    grade = fields.Char()

    def get_post_applying_ids_json(self):
        for record in self:
            record.post_applying_ids_json = json.dumps(record.post_applying.ids)

    def get_medium_ids_json(self):
        for record in self:
            record.medium_ids_json = json.dumps(record.medium.ids)

    def button_inactive(self):
        for rec in self:
            rec.state = 'inactive'
    def button_active(self):
        for rec in self:
            rec.state = 'active'

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == _('/'):
            vals['name'] = self.env['ir.sequence'].next_by_code('job.seeker') or _('/')
        return super(MemberJobSeeker, self).create(vals)



    def send_push_to_job_provider(self):
        """Send push notification to matching Job Providers when this seeker applies."""
        for seeker in self:
            # Find matching job providers (active + matching post or skills)
            matching_providers = self.env['member.job.provider'].sudo().search([
                ('state', '=', 'active'),
                ('required_till', '>=', fields.Date.today()),
                '|',
                    ('skill_ids', 'in', seeker.skill_ids.ids),
                    ('post_required_id', '=', seeker.post_applying_id.id)
            ])

            if not matching_providers:
                _logger.info("No matching providers for seeker %s", seeker.name)
                continue

            # Prepare push content
            title = "New Job Seeker Applied"
            body = f"{seeker.member_name} has applied for {seeker.post_applying_id.name or 'a position'}"
            category_id = seeker.post_applying_id.id or 0
            source = "Job Seeker Application"
            send_url = f"https://new.thesica.in/homepage/jobseeker/details/:{seeker.id}?category_id={category_id}"

            # Log the push
            self.env['push.notification.log.history'].sudo().create({
                'source': source,
                'date_send': fields.Datetime.now(),
            })

            # Send push to each matching provider
            for provider in matching_providers:
                if provider.member_id and provider.member_id.token:
                    try:
                        message = messaging.Message(
                            token=provider.member_id.token,
                            notification=messaging.Notification(
                                title=title,
                                body=body,
                            ),
                            data={"url": send_url}
                        )
                        response = messaging.send(message)
                        _logger.info(f"Push sent to provider {provider.member_name}: {response}")
                    except UnregisteredError:
                        _logger.warning(f"Unregistered token for {provider.member_name}")
                        provider.member_id.token = False
                    except Exception as e:
                        _logger.error(f"Failed to send push to {provider.member_name}: {str(e)}")