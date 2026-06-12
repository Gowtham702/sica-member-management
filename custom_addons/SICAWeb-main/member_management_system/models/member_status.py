from odoo import models, fields, api
from datetime import timedelta


class MemberStatus(models.Model):
    _name = 'member.status'
    _description = 'Member Status'
    _order = 'create_date desc'

    member_id = fields.Many2one(
        'res.member',
        string='Member',
        required=True
    )

    caption = fields.Text(
        string='Caption'
    )

    media_type = fields.Selection([
        ('image', 'Image'),
        ('video', 'Video')
    ],
        string='Media Type',
        default='image',
        required=True
    )

    media_file = fields.Binary(
        string='Image / Video',
        attachment=True,
        required=True
    )

    media_filename = fields.Char(
        string='File Name'
    )

    expiry_time = fields.Datetime(
        string='Expiry Time',
        readonly=True
    )

    status_url = fields.Char(
        string='Status Preview URL',
        compute='_compute_status_url'
    )

    status_preview = fields.Html(
        string='Status Preview',
        compute='_compute_status_preview',
        sanitize=False
    )

    @api.depends('media_file')
    def _compute_status_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url.image'
        ) or self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url'
        ) or ''

        base_url = base_url.replace(
            '0.0.0.0:8069',
            'localhost:8059'
        ).rstrip('/')

        for rec in self:
            if rec.id:
                rec.status_url = "%s/get/status/media/%s" % (
                    base_url,
                    rec.id
                )
            else:
                rec.status_url = False

    @api.depends('media_type', 'status_url')
    def _compute_status_preview(self):
        for rec in self:
            rec.status_preview = ''

            if not rec.status_url:
                continue

            if rec.media_type == 'image':
                rec.status_preview = """
                    <img src="%s"
                         style="max-width:500px;
                                max-height:350px;
                                border-radius:10px;"/>
                """ % rec.status_url

            elif rec.media_type == 'video':
                rec.status_preview = """
                    <video width="500" height="350" controls preload="metadata">
                        <source src="%s" type="video/mp4"/>
                        Your browser does not support video.
                    </video>
                """ % rec.status_url

    @api.model
    def create(self, vals):
        if not vals.get('expiry_time'):
            vals['expiry_time'] = (
                fields.Datetime.now() +
                timedelta(hours=24)
            )

        return super(MemberStatus, self).create(vals)