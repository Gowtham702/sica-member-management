from odoo import models, fields, api
from odoo.exceptions import UserError

class SmsOtp(models.Model):
    _name = 'sms.otp'
    _description = 'Sms Otp'
    _order = 'id desc'

    account_type = fields.Selection([
        ('member', 'Member'),
        ('guest', 'Guest')
    ])
    guest_name = fields.Char()
    mobile_number = fields.Char()
    member_id = fields.Many2one('res.member')
    membership_number = fields.Char()
    otp_number = fields.Char()
    return_value = fields.Text()
    access_token = fields.Char()
    is_session_status = fields.Selection([
        ('Open', 'Open'),
        ('Close', 'Close'),
        ('Request_Sent', 'Request Sent')
    ])
