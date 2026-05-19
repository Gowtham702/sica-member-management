from odoo import models,fields,api,_

class GalleryCategory(models.Model):
    _name = 'sica.gallery.category'
    _description = 'Sica Gallery Category'

    name = fields.Char()
    description = fields.Char()

class Gallery(models.Model):
    _name = 'sica.gallery'
    _description = ' Sica Gallery'
    _inherit = ['mail.activity.mixin', 'avatar.mixin']

    category_id = fields.Many2one('sica.gallery.category')
    description = fields.Html()
    name = fields.Char(string='Gallery Name')
    date = fields.Date()
    photo = fields.Binary()
    attachments_ids = fields.Many2many('ir.attachment', public=True)
    gallery_like_ids = fields.One2many('gallery.like', 'gallery_id')
    gallery_comment_ids = fields.One2many('gallery.comment', 'gallery_id')
    gallery_image_ids = fields.One2many('gallery.image', 'gallery_id', coloum1='gallery_id', coloum2='image', string='Images')

class GalleryLike(models.Model):
    _name = 'gallery.like'
    _description = 'Gallery Like'

    member_id = fields.Many2one('res.member')
    member_name = fields.Char()
    remark = fields.Char()
    gallery_id = fields.Many2one('sica.gallery')


class GalleryComment(models.Model):
    _name = 'gallery.comment'
    _description = 'Gallery Comment'
    _inherit = ['mail.activity.mixin', 'avatar.mixin']

    name = fields.Char()
    member_id = fields.Many2one('res.member')
    member_name = fields.Char()
    remark = fields.Char()
    gallery_id = fields.Many2one('sica.gallery')
    request_type = fields.Selection([
        ('Create', 'Create'),
        ('Update', 'Update'),
        ('Delete', 'Delete')
    ])
    approve_status = fields.Selection([
        ('Waiting_for_Approval', 'Waiting for Approval'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ])
    duplicate_gallery_id = fields.Many2one('sica.gallery')
    comment_id = fields.Many2one('gallery.comment')
    gallery_image = fields.Binary(string="Image")

    def action_approve(self):
        for rec in self:
            if rec.request_type == 'Create':
                rec.gallery_id = rec.duplicate_gallery_id
                rec.approve_status = 'Approved'
            elif rec.request_type == 'Update':
                if rec.request_type == 'Update':
                    rec.gallery_id = rec.duplicate_gallery_id
                    rec.comment_id.sudo().unlink()
                    rec.approve_status = 'Approved'
            else:
                if self.request_type == 'Delete':
                    rec.sudo().unlink()
                    rec.approve_status = 'Approved'
    def action_reject(self):
        for rec in self:
            rec.approve_status = 'Rejected'


class GalleryImage(models.Model):
    _name = 'gallery.image'
    _description = 'Gallery Image'

    title = fields.Char('Title', required=True)
    description = fields.Char('Description')
    image = fields.Binary('Image')
    gallery_id = fields.Many2one('sica.gallery')



