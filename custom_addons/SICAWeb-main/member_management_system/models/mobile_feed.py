from odoo import models, fields


class SicaMobilePost(models.Model):
    _name = 'sica.mobile.post'
    _description = 'SICA Mobile Post'
    _order = 'create_date desc'

    member_id = fields.Many2one('res.member', string='Member', required=True)
    text = fields.Text(string='Post Text')
    image = fields.Binary(string='Image', attachment=True)
    image_filename = fields.Char(string='Image Filename')
    comments_count = fields.Integer(string='Comments Count', default=0)
    share_count = fields.Integer(string='Share Count', default=0)
    reaction_count = fields.Integer(string='Reaction Count', default=0)


class SicaMobileShooting(models.Model):
    _name = 'sica.mobile.shooting'
    _description = 'SICA Mobile Shooting'
    _order = 'create_date desc'

    title = fields.Char(string='Title', required=True)
    description = fields.Text(string='Description')
    image = fields.Binary(string='Image', attachment=True)
    image_filename = fields.Char(string='Image Filename')
    location = fields.Char(string='Location')
    production_house = fields.Char(string='Production House')
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')

    status = fields.Selection([
        ('pre_production', 'Pre Production'),
        ('shooting', 'Shooting'),
        ('completed', 'Completed'),
    ], string='Status', default='pre_production')

    team_member_ids = fields.Many2many(
        'res.member',
        string='Team Members'
    )


class SicaMobileRequirement(models.Model):
    _name = 'sica.mobile.requirement'
    _description = 'SICA Mobile Requirement'
    _order = 'create_date desc'

    member_id = fields.Many2one('res.member', string='Member', required=True)

    requirement_type = fields.Selection([
        ('job_post', 'Job Post'),
        ('job_apply', 'Job Apply'),
        ('event', 'Event'),
        ('equipment', 'Equipment'),
        ('marketplace', 'Marketplace'),
    ], string='Requirement Type', default='job_post')

    title = fields.Char(string='Title', required=True)
    description = fields.Text(string='Description')
    location = fields.Char(string='Location')
    event_date = fields.Date(string='Event Date')
    experience = fields.Char(string='Experience')