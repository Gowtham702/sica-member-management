from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import content_disposition
import base64


class MemberQRController(http.Controller):

    @http.route('/member/qr_code/<string:membership_no>', type='http', auth='public', website=True)
    def qr_code_scan(self, membership_no, **kwargs):
        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_no)])
        result, format = request.env.ref('member_management_system.action_report_member_pdf')._render_qweb_pdf(
            res_ids=member.id)
        result = base64.b64encode(result)
        report_name = "Member Details %s" % str(member.membership_no)
        vals = {}
        vals['name'] = report_name + '.pdf'
        vals['type'] = 'binary'
        vals['datas'] = result
        vals['store_fname'] = report_name + '.pdf'
        vals['mimetype'] = 'application/pdf'
        vals['index_content'] = 'image'
        vals['res_model'] = 'res.member'
        vals['res_id'] = member.membership_no
        vals['public'] = True
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url.image')
        attachment = request.env['ir.attachment'].sudo().search(
            [('res_model', '=', 'res.member'), ('res_id', '=', member.membership_no),
             ('name', '=', report_name + '.pdf')], limit=1)
        if attachment:
            attachment.sudo().write(vals)

        if member:
            attachment_url = '%s/web/content/%s' % (base_url, member.attachment_id.id)
            return request.redirect(attachment_url)
        else:
            return "Member not found."

