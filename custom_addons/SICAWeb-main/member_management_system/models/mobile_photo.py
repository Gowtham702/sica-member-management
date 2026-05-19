from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError

class MObilePhoto(models.Model):
    _name = 'mobile.photo'
    _inherit = ["mail.thread", "mail.activity.mixin", "format.address.mixin", "avatar.mixin"]
    _description = 'Mobile Photo'

    name = fields.Char()
    photo = fields.Binary(attachment=True,
        help='Upload an image',)
    promotion_link = fields.Char()
    image_note = fields.Char(default='16:4')
