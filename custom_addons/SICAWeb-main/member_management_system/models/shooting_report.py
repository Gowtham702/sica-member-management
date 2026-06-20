from odoo import models, fields


class ShootingDailyReport(models.Model):
    _name = 'shooting.daily.report'
    _description = 'Shooting Daily Report'
    _order = 'report_date desc, id desc'

    shooting_id = fields.Many2one('sica.mobile.shooting', string='Shooting', required=True, ondelete='cascade')
    member_id = fields.Many2one('res.member', string='Member')
    report_date = fields.Date(string='Report Date', required=True)
    remarks = fields.Text(string='Remarks')

    approval_status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='pending')

    approved_by_member_id = fields.Many2one('res.member', string='Approved By')
    approval_remarks = fields.Text(string='Approval Remarks')

    image_ids = fields.One2many(
        'shooting.daily.report.image',
        'report_id',
        string='Images'
    )


class ShootingDailyReportImage(models.Model):
    _name = 'shooting.daily.report.image'
    _description = 'Shooting Daily Report Image'

    report_id = fields.Many2one('shooting.daily.report', string='Report', required=True, ondelete='cascade')
    image = fields.Binary(string='Image', required=True)
    image_filename = fields.Char(string='Filename')