from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MemberPaymentRequest(models.Model):
    _name = 'member.payment.request'
    _inherit = ["mail.thread", "mail.activity.mixin", "format.address.mixin", "avatar.mixin"]

    _description = 'Member Payment Request'

    name = fields.Char(string='Reference', default='/', readonly=True)
    membership_no = fields.Char()
    member_name = fields.Char()
    amount = fields.Char()
    payment_link = fields.Char()
    contact_no = fields.Char()
    note = fields.Text()
    remark = fields.Text()
    member_id = fields.Many2one('res.member')
    event_id = fields.Many2one('shooting.event')
    event_name = fields.Char(related='event_id.title')

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == _('/'):
            vals['name'] = self.env['ir.sequence'].next_by_code('payment.request') or _('/')
        return super(MemberPaymentRequest, self).create(vals)
