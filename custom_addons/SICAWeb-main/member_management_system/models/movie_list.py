from odoo import api,models,fields
import base64
import tempfile
import xlrd
from datetime import datetime

class MyMovieList(models.Model):
    _name = 'movie.list'
    _description = 'My Movie list'
    _rec_name = 'movie_name'

    # def default_get(self, fields):
    #     res = super(MyMovieList, self).default_get(fields)
    #
    #     if 'sequence' in fields:
    #         # fallback project_type (default = "movies")
    #         project_type = res.get("project_type", "movies")
    #
    #         # find last sequence only for this project_type
    #         last_record = self.env['movie.list'].search(
    #             [('project_type', '=', project_type)],
    #             order="sequence desc",
    #             limit=1
    #         )
    #
    #         res['sequence'] = (last_record.sequence + 1) if last_record else 1
    #
    #     return res

    # @api.onchange('project_type')
    # def _onchange_project_type(self):
    #     if self.project_type:
    #         last_record = self.env['movie.list'].search(
    #             [('project_type', '=', self.project_type)],
    #             order="sequence desc",
    #             limit=1
    #         )
    #
    #         if last_record:
    #             self.sequence = last_record.sequence + 1
    #         else:
    #             self.sequence = 1

    movie_name = fields.Char(string="Title", required=False)
    # project_type = fields.Selection([
    #     ("film", "Film"),("series", "Series"),
    #     ("serial", "Serial"),("others", "Others Etc.,"),
    # ], default="movies", copy=False, string="Project Type")
    project_type = fields.Char(string="Project Type")
    date = fields.Date(string="Date")
    production_companies = fields.Char(string="Production Company")
    dop_name = fields.Char(string="DOP Name")
    team_member = fields.Char(string="Team Members")
    title = fields.Char(string="Title")
    channel_name = fields.Char(string="Channel Name")
    sequence = fields.Integer(string="Sequence")
    movie_link = fields.Char(string="Movie Link", help="Enter the URL or link to the movie resource (e.g., YouTube, website, etc.)")

    image = fields.Binary(string="Image", store=True)
    image_note = fields.Char(default='16:6 or 1:1')
    # state = fields.Selection([
    #     ("on_going", "On-Going"),
    #     ("completed", "Released"),
    # ], default="on_going", copy=False, string="Status")
    # member_type = fields.Selection([
    #     ("member", "Member"),
    #     ("non_member", "Non-Member"),
    # ])
    member_type = fields.Char(string="Member Type")
    language = fields.Char(string="Language")
    # member_state = fields.Selection([
    #     ('Member', 'Member'),
    #     ('Non-Member', 'Non-Member'),
    # ])
    membership_no = fields.Char(string="Membership No.")
    # grade = fields.Selection([
    #     ('Life', 'Life'),
    #     ('Active', 'Active'),
    #     ('Associate', 'Associate'),
    #     ('Junior', 'Junior'),
    # ])
    grade = fields.Char(string="Grade")
    # release_state = fields.Selection([
    #     ('Released', 'Released'),
    #     ('Not Released', 'Not Released'),
    # ])
    release_state = fields.Char(string="Release State")
    # dop_team = fields.Char(string="DOP Team")

    # def action_approve(self):
    #     self.write({
    #         'state': 'completed',
    #     })