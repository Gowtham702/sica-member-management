from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
from firebase_admin import messaging
from firebase_admin._messaging_utils import UnregisteredError
import logging

_logger = logging.getLogger(__name__)

class GrievanceReason(models.Model):
    _name = 'grievance.reason'
    _inherit = ["mail.thread", "mail.activity.mixin", "format.address.mixin", "avatar.mixin"]
    _description = 'Grievance Reason'

    name = fields.Char()
    is_production_update = fields.Boolean()

class GrievanceReport(models.Model):
    _name = 'grievance.report'
    _inherit = ["mail.thread", "mail.activity.mixin", "format.address.mixin", "avatar.mixin"]
    _description = 'Grievance Report'
    _rec_name = 'reference'

    name = fields.Char()
    grievance_reason_id = fields.Many2one('grievance.reason')
    member_id = fields.Many2one('res.member')
    reference = fields.Char(string='Reference', default='/', readonly=True)
    member_name_no = fields.Char()
    project_name = fields.Char()
    projection_house_name = fields.Char()
    outdoor_unit_name = fields.Char()
    location = fields.Char()
    issue_raised = fields.Selection([
        ('Camera', 'Camera'),
        ('Lens', 'Lens'),
        ('Lights', 'Lights'),
        ('Grips', 'Grips')
    ])
    issue_type = fields.Char()
    approximate_time_lost = fields.Char()
    contact_outdoor_unit_manager = fields.Char()
    has_outdoor_unit_manager_helpful_to_solve_issue = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ])
    has_outdoor_unit_manager_helpful_to_the_solve_issue = fields.Char()
    issue_has_been_reported = fields.Char()
    name_contact_no_of_production_manager_executive_producer = fields.Char()
    brief_issue_faced_with_service_of_outdoor_unit_equipment = fields.Text()


    @api.model
    def create(self, vals):
        if not vals.get('reference') or vals['reference'] == _('/'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('grievance.report') or _('/')
        return super(GrievanceReport, self).create(vals)

class DailyShootingUpdate(models.Model):
    _name = 'daily.shooting.update'
    _description = 'Daily Shooting Update'
    _rec_name = 'reference'

    reference = fields.Char(string='Reference', default='/', readonly=True)
    email = fields.Char()
    date = fields.Date()
    member_name = fields.Char()
    member_contact_no = fields.Char()
    membership_no = fields.Char()
    category = fields.Char()
    project_title = fields.Char()
    format = fields.Char()
    designation = fields.Char()
    producer = fields.Char()
    project_house = fields.Char()
    production_executive = fields.Char()
    production_executive_contact_no = fields.Char()
    outdoor_unit_name = fields.Char()
    location = fields.Char()
    grievance_reason_id = fields.Many2one('grievance.reason')
    member_id = fields.Many2one('res.member')

    # Approval fields
    is_dop_approved = fields.Boolean(string="DoP Approved", tracking=True)
    is_admin_approved = fields.Boolean(string="SICA Admin Approved", tracking=True)


    @api.model
    def create(self, vals):
        if not vals.get('reference') or vals['reference'] == _('/'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('shooting.update') or _('/')
        return super(DailyShootingUpdate, self).create(vals)
    
    def action_approve_dop(self):
        for record in self:
            record.is_dop_approved = True

            title = "Shooting Update Approved"
            body = f"The shooting update '{record.reference}' has been approved by DoP."
            source = "DoP Approval"

            record.update_notification(title, body, source)


    def action_approve_admin(self):
        for record in self:
            record.is_admin_approved = True

            title = "Shooting Update Approved"
            body = f"The shooting update '{record.reference}' has been approved by DoP."
            source = "Admin Approval"

            record.update_notification(title, body, source)

        
    def update_notification(self, title, body, source):
            _logger.info(f"Sending push notification for DailyShootingUpdate: {title}")
            print("11111111111111111111111111111111111111111111111")
            print("Title: ",title, body, source)
            # Log the push notification history
            self.env['push.notification.log.history'].sudo().create({
                'source': source,
                'date_send': fields.Datetime.now(),
            })

            # Example URL - customize for your frontend
            send_id = f"https://new.thesica.in/homepage/dailyshooting/details/?id={self.id}"

            print("send_id: ",send_id)

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