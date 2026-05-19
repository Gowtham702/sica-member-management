from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError

class MemberMedium(models.Model):
    _name = 'member.medium'
    _description = 'Member Medium'

    name = fields.Char()