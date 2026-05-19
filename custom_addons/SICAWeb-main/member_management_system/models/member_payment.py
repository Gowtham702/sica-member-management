from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MemberPayment(models.Model):
    _name = 'member.payment'
    _inherit = ["mail.thread", "mail.activity.mixin", "format.address.mixin", "avatar.mixin"]

    _description = 'Member Payment'

    name = fields.Char(string='Reference', default='/', readonly=True)
    order_id = fields.Char()
    order_amount = fields.Float()
    payment_link_id = fields.Char()
    payment_link_url = fields.Char()
    payment_status = fields.Char()
    amount_paid = fields.Float()
    note = fields.Text()
    remark = fields.Text()
    member_id = fields.Many2one('res.member')

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == _('/'):
            vals['name'] = self.env['ir.sequence'].next_by_code('member.payment') or _('/')
        return super(MemberPayment, self).create(vals)
