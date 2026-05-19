from odoo import api,models,fields

class SicaBlog(models.Model):
    _name = 'sica.blog'
    _description = 'Sica Blog'
    _rec_name = 'title'
    _order = 'sequence desc'

    def default_get(self, fields):
        res = super(SicaBlog, self).default_get(fields)
        if 'sequence' in fields:
            last_seq = self.env['sica.blog'].search([], order="sequence desc", limit=1).sequence
            res['sequence'] = last_seq + 1 if last_seq else 1
        return res

    title = fields.Char()
    date = fields.Date()
    views = fields.Integer()
    sequence = fields.Integer()
    description = fields.Html()
    image = fields.Binary()
    image_note = fields.Char(default='16:6 or 1:1')

    @api.model
    def create(self, vals):
        if vals.get('title'):
            title = str(vals.get('title')) or ''
            body = str(vals.get('title')) or ''
        else:
            title = 'New Blog created'
            body = 'New Blog created'
        title = 'Blog added'
        source = 'SICA Blog'
        # self.update_notification(title, body, source)
        return super(SicaBlog, self).create(vals)

    def update_notification(self, title, body, source):
        send = self.env['push.notification.log.history'].sudo().create({
            'source': 'SICA Blog',
            'date_send': fields.Datetime.now(),
        })
        send_id = "https://new.thesica.in/homepage/newstabbarwidget/blogs?title="+title
        if send:
            send.send_notification(title, body, source, send_id)


class SicaFeatures(models.Model):
    _name = 'sica.features'
    _description = 'Sica Features'
    _rec_name = 'title'

    def default_get(self, fields):
        res = super(SicaFeatures, self).default_get(fields)
        if 'sequence' in fields:
            last_seq = self.env['sica.features'].search([], order="sequence desc", limit=1).sequence
            res['sequence'] = last_seq + 1 if last_seq else 1
        return res

    title = fields.Char()
    date = fields.Date()
    views = fields.Integer()
    sequence = fields.Integer()
    description = fields.Html()
    attachments_ids = fields.Many2many('ir.attachment', public=True)
    image_note = fields.Char(default='16:6 or 1:1')
