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


class SicaMobileComment(models.Model):
    _name = 'sica.mobile.comment'
    _description = 'SICA Mobile Comment'
    _order = 'create_date desc'

    post_id = fields.Many2one('sica.mobile.post', string='Post', required=True, ondelete='cascade')
    member_id = fields.Many2one('res.member', string='Member', required=True)
    comment = fields.Text(string='Comment', required=True)


class SicaMobileReaction(models.Model):
    _name = 'sica.mobile.reaction'
    _description = 'SICA Mobile Reaction'

    post_id = fields.Many2one('sica.mobile.post', string='Post', required=True, ondelete='cascade')
    member_id = fields.Many2one('res.member', string='Member', required=True)
    reaction = fields.Selection([
        ('like', 'Like'),
        ('love', 'Love'),
        ('haha', 'Haha'),
        ('wow', 'Wow'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
    ], string='Reaction', default='like')

    _sql_constraints = [
        ('unique_post_member_reaction', 'unique(post_id, member_id)', 'Member already reacted to this post.')
    ]


class SicaMobileFollow(models.Model):
    _name = 'sica.mobile.follow'
    _description = 'SICA Mobile Follow'
    _order = 'create_date desc'

    follower_id = fields.Many2one('res.member', string='Follower', required=True, ondelete='cascade')
    following_id = fields.Many2one('res.member', string='Following', required=True, ondelete='cascade')

    _sql_constraints = [
        ('unique_follow', 'unique(follower_id, following_id)', 'Already following this member.')
    ]


class SicaMobileShooting(models.Model):
    _name = 'sica.mobile.shooting'
    _description = 'SICA Mobile Shooting'
    _order = 'create_date desc'
    member_id = fields.Many2one('res.member', string='Member')

    title = fields.Char(string='Title', required=True)
    description = fields.Text(string='Description')
    image = fields.Binary(string='Image', attachment=True)
    image_filename = fields.Char(string='Image Filename')
    movie_poster = fields.Binary(string='Movie Poster', attachment=True)
    movie_poster_filename = fields.Char(string='Movie Poster Filename')
    location = fields.Char(string='Location')
    production_house = fields.Char(string='Production House')
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    status = fields.Selection([
        ('pre_production', 'Pre Production'),
        ('shooting', 'Shooting'),
        ('completed', 'Completed'),
    ], string='Status', default='pre_production')
    team_member_ids = fields.Many2many('res.member', string='Team Members')


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

class SicaMobileComment(models.Model):
    _name = 'sica.mobile.comment'
    _description = 'SICA Mobile Comment'
    _order = 'create_date desc'

    post_id = fields.Many2one('sica.mobile.post', required=True, ondelete='cascade')
    member_id = fields.Many2one('res.member', required=True)
    comment = fields.Text(required=True)


class SicaMobilePostAction(models.Model):
    _name = 'sica.mobile.post.action'
    _description = 'SICA Mobile Post Action'
    _order = 'create_date desc'

    post_id = fields.Many2one('sica.mobile.post', required=True, ondelete='cascade')
    member_id = fields.Many2one('res.member', required=True)
    action_type = fields.Selection([
        ('like', 'Like'),
        ('love', 'Love'),
        ('haha', 'Haha'),
        ('wow', 'Wow'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
    ], default='like')

    _sql_constraints = [
        ('unique_post_member_action', 'unique(post_id, member_id)', 'Already reacted.')
    ]


class SicaMobileFollow(models.Model):
    _name = 'sica.mobile.follow'
    _description = 'SICA Mobile Follow'
    _order = 'create_date desc'

    follower_id = fields.Many2one('res.member', required=True, ondelete='cascade')
    following_id = fields.Many2one('res.member', required=True, ondelete='cascade')

    _sql_constraints = [
        ('unique_follow_member', 'unique(follower_id, following_id)', 'Already following.')
    ]
class SicaCommonComment(models.Model):
    _name = 'sica.common.comment'
    _description = 'SICA Common Comment'
    _order = 'create_date desc'

    source_type = fields.Selection([
        ('news', 'News'),
        ('blog', 'Blog'),
        ('tech_talk', 'Tech Talk'),
        ('gallery', 'Gallery'),
    ], required=True)

    source_id = fields.Integer(required=True)

    member_id = fields.Many2one(
        'res.member',
        required=True,
        ondelete='cascade'
    )

    comment = fields.Text(required=True)
    active = fields.Boolean(default=True)
    source_id = fields.Integer(required=True)
    member_id = fields.Many2one('res.member', required=True)
