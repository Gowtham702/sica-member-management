from odoo import models, fields, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import re


class SicaMember(models.Model):
    _name = 'sica.member'
    _description = 'SICA Member'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'member_id desc'

    # Basic Fields
    member_id = fields.Char(
        string='Member ID',
        readonly=True,
        default='New',
        copy=False,
        tracking=True
    )
    name = fields.Char(string='Member Name', required=True, tracking=True)
    mobile = fields.Char(string='Mobile Number', required=True)
    email = fields.Char(string='Email', required=True, tracking=True)
    address = fields.Text(string='Address')
    company_name = fields.Char(string='Company Name')
    designation = fields.Char(string='Designation')
    profile_photo = fields.Binary(string='Profile Photo', attachment=True)
    profile_photo_filename = fields.Char(string='Photo Filename')

    # Membership Fields
    membership_type_id = fields.Many2one(
        'sica.membership.type',
        string='Membership Type',
        required=True,
        tracking=True
    )
    joining_date = fields.Date(
        string='Joining Date',
        default=fields.Date.today,
        required=True
    )
    expiry_date = fields.Date(
        string='Expiry Date',
        compute='_compute_expiry_date',
        store=True
    )

    # Status Field
    status = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired'),
    ], string='Status', default='active', tracking=True, compute='_compute_status', store=True)

    notes = fields.Text(string='Notes')

    # -------------------------
    # ORM: Auto-generate Member ID
    # -------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('member_id', 'New') == 'New':
                vals['member_id'] = self.env['ir.sequence'].next_by_code('sica.member') or 'New'
        return super().create(vals_list)

    # -------------------------
    # ORM: Compute Expiry Date
    # -------------------------
    @api.depends('joining_date', 'membership_type_id')
    def _compute_expiry_date(self):
        for rec in self:
            if rec.joining_date and rec.membership_type_id:
                rec.expiry_date = rec.joining_date + relativedelta(
                    months=rec.membership_type_id.duration_months
                )
            else:
                rec.expiry_date = False

    # -------------------------
    # ORM: Compute Status
    # -------------------------
    @api.depends('expiry_date')
    def _compute_status(self):
        today = fields.Date.today()
        for rec in self:
            if rec.expiry_date and rec.expiry_date < today:
                rec.status = 'expired'
            else:
                rec.status = 'active'

    # -------------------------
    # ORM: Email Validation
    # -------------------------
    @api.constrains('email')
    def _validate_email(self):
        email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        for rec in self:
            if rec.email and not email_pattern.match(rec.email):
                raise ValidationError(f"Invalid email address: {rec.email}")

    # -------------------------
    # Smart Button: Total Members
    # -------------------------
    def action_total_members(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'All Members',
            'res_model': 'sica.member',
            'view_mode': 'list,form',
        }

    # -------------------------
    # Print Report Action
    # -------------------------
    def action_print_member_report(self):
        return self.env.ref('member_management.action_member_report').report_action(self)
