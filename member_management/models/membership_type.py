from odoo import models, fields


class MembershipType(models.Model):
    _name = 'sica.membership.type'
    _description = 'Membership Type'
    _order = 'name'

    name = fields.Char(string='Membership Type', required=True)
    duration_months = fields.Integer(string='Duration (Months)', default=12)
    fee = fields.Float(string='Membership Fee', default=0.0)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)

    member_count = fields.Integer(
        string='Total Members',
        compute='_compute_member_count'
    )

    def _compute_member_count(self):
        for rec in self:
            rec.member_count = self.env['sica.member'].search_count([
                ('membership_type_id', '=', rec.id)
            ])
