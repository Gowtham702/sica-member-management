from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError

class DiscussCategory(models.Model):
    _name = 'discuss.category'
    _inherit = ["mail.thread", "mail.activity.mixin", "format.address.mixin", "avatar.mixin"]
    _description = 'Discuss Category'

    name = fields.Char()
    description = fields.Text()


class DiscussionForum(models.Model):
    _name = 'discussion.forum'
    _inherit = ["mail.thread", "mail.activity.mixin", "format.address.mixin", "avatar.mixin"]
    _description = 'Discussion Forum'

    name = fields.Char()
    category_id = fields.Many2one('discuss.category')
    discussion_topic = fields.Text()
    member_id = fields.Many2one('res.member')
    user_id = fields.Many2one(
        'res.users', string='Responsible', tracking=True,
        default=lambda self: self.env.user)
    discussion_comment_ids = fields.One2many('discussion.comment', 'discussion_id')

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == _('/'):
            vals['name'] = self.env['ir.sequence'].next_by_code('discussion.forum') or _('/')
        return super(DiscussionForum, self).create(vals)


class DiscussionComments(models.Model):
    _name = 'discussion.comment'
    _description = 'Discussion Comments'

    member_id = fields.Many2one('res.member')
    comment = fields.Text()
    discussion_id = fields.Many2one('discussion.forum')
    document = fields.Char()
    image = fields.Binary()
    child_comment_ids = fields.One2many('child.discussion.comment', 'comment_id')

class ChildDiscussionComments(models.Model):
    _name = 'child.discussion.comment'
    _description = 'Child Discussion Comments'

    member_id = fields.Many2one('res.member')
    comment = fields.Text()
    discussion_id = fields.Many2one('discussion.forum')
    document = fields.Char()
    image = fields.Binary()
    comment_id = fields.Many2one('discussion.comment')



