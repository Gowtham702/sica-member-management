from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError

class ShootingTitle(models.Model):
    _name = 'shooting.title'
    _description = 'Shooting Title'

    name = fields.Char()
    shooting_ids = fields.One2many('sica.shooting', 'shooting_title_id')
    member_id = fields.Many2one('res.member')

class ShootingImage(models.Model):
    _name = 'shooting.image'
    _description = 'Shooting Image'

    name = fields.Text()
    image = fields.Binary()


class ShootingDetails(models.Model):
    _name = 'sica.shooting'
    _description = 'Sica Shooting'

    name = fields.Char(string='Reference', default='/', readonly=True)
    project_title = fields.Char()
    medium = fields.Char()
    start_date = fields.Date()
    end_date = fields.Date()
    member_id = fields.Many2one('res.member')
    choose_dop_for_approval = fields.Selection([
        ('YES', 'YES'),
        ('NO', 'NO')
    ])
    dop_member_id = fields.Many2one('res.member')

    date = fields.Date()
    member_name = fields.Char()
    member_number = fields.Char()
    mobile_number = fields.Char()
    grade = fields.Char()
    dop_name = fields.Char()
    dop_number = fields.Char()
    shooting_title_id = fields.Many2one('shooting.title')
    medium_id = fields.Many2one('member.medium')
    designation = fields.Char()
    producer = fields.Char()
    production_house = fields.Char()
    production_executive = fields.Char()
    production_executive_contact_no = fields.Char()
    location = fields.Char()
    outdoor_unit_name = fields.Char()
    notes = fields.Text()
    state = fields.Selection([
        ('Shooting Updated', "Shooting Updated"),
        ('Waiting For Dop Approval', 'Waiting For Dop Approval'),
        ('Dop Approved', 'Dop Approved'),
        ('Reject', 'DOP Reject')
    ], default='Dop Approved', string='Status')

    def action_dop_approved(self):
        for rec in self:
            rec.state = 'Dop Approved'

    def action_dop_reject(self):
        for rec in self:
            rec.state = 'Reject'


    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == _('/'):
            vals['name'] = self.env['ir.sequence'].next_by_code('sica.shooting') or _('/')
        return super(ShootingDetails, self).create(vals)


class ShootingDop(models.Model):
    _name = 'shooting.dop'
    _description = 'Shooting DOP'

    name = fields.Char(string='Reference', default='/', readonly=True)
    shooting_id = fields.Many2one('sica.shooting')
    designation = fields.Char()
    project_title = fields.Char()
    member_id = fields.Many2one('res.member')
    medium = fields.Char()
    start_date = fields.Date()
    end_date = fields.Date()
    outdoor_link_details = fields.Text()
    associate_ids = fields.One2many('shooting.associate', 'shooting_id')
    attending = fields.Boolean()
    member_contact_no = fields.Char()
    email = fields.Char()
    membership_no = fields.Char()
    producer = fields.Char()
    production_house = fields.Char()
    production_executive = fields.Char()
    production_executive_contact_no = fields.Char()
    location = fields.Char()

    date = fields.Date()
    member_name = fields.Char()
    member_number = fields.Char()
    mobile_number = fields.Char()
    grade = fields.Char()
    shooting_title_id = fields.Many2one('shooting.title')
    medium_id = fields.Many2one('member.medium')
    schedule_start = fields.Date()
    schedule_end = fields.Date()
    outdoor_unit_name = fields.Char()

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == _('/'):
            vals['name'] = self.env['ir.sequence'].next_by_code('shooting.dop') or _('/')
        return super(ShootingDop, self).create(vals)

class ShootingAssociate(models.Model):
    _name = 'shooting.associate'
    _description = 'Shooting Associate'

    name = fields.Char()
    role_type = fields.Selection([
        ('Associate', 'Associate'),
        ('Assistant', 'Assistant'),
        ('Operative', 'Operative')
    ])
    member_role_tpe = fields.Char()
    mobile_number = fields.Char()
    shooting_id = fields.Many2one('shooting.dop')
    member_id = fields.Many2one('res.member')
    member_number = fields.Char()
    attending = fields.Boolean()
    not_attending_reason = fields.Char()


