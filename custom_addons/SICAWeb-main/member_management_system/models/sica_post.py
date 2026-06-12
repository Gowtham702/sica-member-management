from odoo import models, fields

class SicaPost(models.Model):
    _name = 'sica.post'
    _description = 'SICA Post'

    title = fields.Char(required=True)
    description = fields.Text()

    comments = fields.Integer(default=0)
    shares = fields.Integer(default=0)
    reactions = fields.Integer(default=0)

    image = fields.Binary()
    image_filename = fields.Char()
    