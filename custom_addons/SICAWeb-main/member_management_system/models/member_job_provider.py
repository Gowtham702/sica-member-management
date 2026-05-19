
import firebase_admin
from firebase_admin import messaging
from firebase_admin._messaging_utils import UnregisteredError
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)

class MemberJobProvider(models.Model):
    _name = 'member.job.provider'
    _inherit = ["mail.thread", "mail.activity.mixin", "format.address.mixin", "avatar.mixin"]

    _description = 'Member Job Provider'

    name = fields.Char(string='Reference', default='/', readonly=True)
    member_id = fields.Many2one('res.member')
    mobile_number = fields.Char()
    member_name = fields.Char()
    membership_no = fields.Char()
    designation = fields.Char()
    experience = fields.Char()
    skill = fields.Text()
    medium = fields.Many2many('member.medium')
    portifolio_link = fields.Char()
    project_requirement = fields.Many2many('job.title')
    note = fields.Text()
    profile_pic = fields.Binary()
    state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], default='active')
    active = fields.Boolean(default='True')
    date = fields.Date()
    available_start_date = fields.Date()
    available_end_date = fields.Date()
    required_from = fields.Date()
    required_till = fields.Date()
    post_required_id = fields.Many2one('job.title')
    medium_id = fields.Many2one('member.medium')
    grade = fields.Char()
    skill_ids = fields.Many2many('member.skill')
    # description = fields.Char()
    # grade = fields.Selection([
    #     ("junior", "Junior"),
    #     ("staff", "Staff"),
    #     ("life", "Life"),
    #     ("active", "Active"),
    #     ("associate", "Associate"),
    # ], string="Grade")


    def button_inactive(self):
        for rec in self:
            rec.state = 'inactive'
    def button_active(self):
        for rec in self:
            rec.state = 'active'

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == _('/'):
            vals['name'] = self.env['ir.sequence'].next_by_code('job.provider') or _('/')
        return super(MemberJobProvider, self).create(vals)

    def action_find_job_seeker(self):
        for rec in self:
            job_seeker_ids = []
            if rec.required_till < fields.Date.today():
                raise UserError(_('Post already expired'))
            filter_by_date = self.env['member.job.seeker'].search([('till_date', '<=', rec.required_till)])
            for job_seeker in filter_by_date:
                if any(skill.id in rec.skill_ids.ids for skill in job_seeker.skill_ids):
                    job_seeker_ids.append(job_seeker.id)
            for job_seeker in filter_by_date:
                if rec.medium_id.id == job_seeker.medium_id.id:
                    job_seeker_ids.append(job_seeker.id)
            for job_seeker in filter_by_date:
                if rec.post_required_id.id == job_seeker.post_applying_id.id:
                    job_seeker_ids.append(job_seeker.id)

            return {
                'type': 'ir.actions.act_window',
                'name': _('Job Seeker'),
                'view_mode': 'tree,form',
                'res_model': 'member.job.seeker',
                'domain': [('id', 'in', job_seeker_ids)],
            }
        
    def send_push_to_job_seekers(self):
            """Send push notification to matching Job Seekers when a new provider posts a job."""
            for provider in self:
                # Find matching job seekers (active + matching post or skills)
                matching_seekers = self.env['member.job.seeker'].sudo().search([
                    ('state', '=', 'active'),
                    ('till_date', '>=', fields.Date.today()),
                    '|',
                        ('skill_ids', 'in', provider.skill_ids.ids),
                        ('post_applying_id', '=', provider.post_required_id.id)
                ])

                if not matching_seekers:
                    _logger.info("No matching seekers for provider %s", provider.name)
                    continue

                # Prepare push content
                title = "New Job Opportunity"
                body = f"{provider.member_name} is hiring for {provider.post_required_id.name or 'a position'}"
                category_id = provider.post_required_id.id or 0
                source = "Job Provider Post"
                send_url = f"https://new.thesica.in/homepage/jobprovider/details/:{provider.id}?category_id={category_id}"

                # Log the push
                self.env['push.notification.log.history'].sudo().create({
                    'source': source,
                    'date_send': fields.Datetime.now(),
                })

                # Send push to each matching seeker
                for seeker in matching_seekers:
                    if seeker.member_id and seeker.member_id.token:
                        try:
                            message = messaging.Message(
                                token=seeker.member_id.token,
                                notification=messaging.Notification(
                                    title=title,
                                    body=body,
                                ),
                                data={"url": send_url}
                            )
                            response = messaging.send(message)
                            _logger.info(f"Push sent to seeker {seeker.member_name}: {response}")
                        except UnregisteredError:
                            _logger.warning(f"Unregistered token for {seeker.member_name}")
                            seeker.member_id.token = False
                        except Exception as e:
                            _logger.error(f"Failed to send push to {seeker.member_name}: {str(e)}")