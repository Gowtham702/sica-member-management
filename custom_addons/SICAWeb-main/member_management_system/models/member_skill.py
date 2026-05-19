from odoo import fields,models,api,_


class JobSkill(models.Model):
    _name = 'member.skill'
    _description = 'Member Skill'

    name = fields.Char()