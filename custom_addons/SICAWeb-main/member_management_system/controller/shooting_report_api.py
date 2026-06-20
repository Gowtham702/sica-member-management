import json
import base64

from odoo import http
from odoo.http import request, Response


class ShootingReportAPI(http.Controller):

    def _json_response(self, data, status=200):
        return Response(
            json.dumps(data),
            status=status,
            content_type='application/json;charset=utf-8'
        )

    def _get_base_url(self):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url.image') or \
                   request.env['ir.config_parameter'].sudo().get_param('web.base.url') or \
                   'http://localhost:8059'
        return base_url.rstrip('/')

    def _get_member_by_no(self, membership_no):
        if not membership_no:
            return request.env['res.member'].sudo()
        return request.env['res.member'].sudo().search([
            ('membership_no', '=', str(membership_no))
        ], limit=1)

    def _report_vals(self, report):
        base_url = self._get_base_url()

        return {
            'id': report.id,
            'shooting_id': report.shooting_id.id,
            'shooting_title': report.shooting_id.title or '',
            'membership_no': report.member_id.membership_no or '',
            'member_name': report.member_id.name or '',
            'report_date': str(report.report_date) if report.report_date else '',
            'remarks': report.remarks or '',
            'approval_status': report.approval_status or '',
            'approved_by_member_no': report.approved_by_member_id.membership_no or '',
            'approved_by_member_name': report.approved_by_member_id.name or '',
            'approval_remarks': report.approval_remarks or '',
            'images': [
                {
                    'id': img.id,
                    'filename': img.image_filename or '',
                    'url': '%s/api/shootings/report/image/%s' % (base_url, img.id),
                }
                for img in report.image_ids
            ],
            'created_date': str(report.create_date),
        }

    @http.route('/api/shootings/report', type='http', auth='public', methods=['POST'], csrf=False)
    def create_shooting_report(self, **post):
        shooting_id = int(post.get('shooting_id') or 0)

        shooting = request.env['sica.mobile.shooting'].sudo().browse(shooting_id)

        if not shooting.exists():
            return self._json_response({
                'success': False,
                'error': 'Shooting not found'
            }, 404)

        member = self._get_member_by_no(post.get('membership_no'))

        approved_member = False
        if post.get('approved_by_member_no'):
            approved_member = self._get_member_by_no(post.get('approved_by_member_no'))

        report = request.env['shooting.daily.report'].sudo().create({
            'shooting_id': shooting.id,
            'member_id': member.id if member else False,
            'report_date': post.get('report_date'),
            'remarks': post.get('remarks') or '',
            'approval_status': post.get('approval_status') or 'pending',
            'approved_by_member_id': approved_member.id if approved_member else False,
            'approval_remarks': post.get('approval_remarks') or '',
        })

        images = request.httprequest.files.getlist('images')

        for img in images:
            request.env['shooting.daily.report.image'].sudo().create({
                'report_id': report.id,
                'image': base64.b64encode(img.read()).decode('utf-8'),
                'image_filename': img.filename,
            })

        return self._json_response({
            'success': True,
            'message': 'Daily report created successfully',
            'report': self._report_vals(report)
        }, 201)

    @http.route('/api/shootings/report', type='http', auth='public', methods=['GET'], csrf=False)
    def get_shooting_reports(self, **kw):
        reports = request.env['shooting.daily.report'].sudo().search([], order='report_date desc, id desc')

        return self._json_response({
            'success': True,
            'count': len(reports),
            'reports': [self._report_vals(r) for r in reports]
        })

    @http.route('/api/shootings/report/<int:report_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_shooting_report_by_id(self, report_id, **kw):
        report = request.env['shooting.daily.report'].sudo().browse(report_id)

        if not report.exists():
            return self._json_response({
                'success': False,
                'error': 'Report not found'
            }, 404)

        return self._json_response({
            'success': True,
            'report': self._report_vals(report)
        })

    @http.route('/api/shootings/report/<int:report_id>', type='http', auth='public', methods=['PUT', 'POST'], csrf=False)
    def update_shooting_report(self, report_id, **post):
        report = request.env['shooting.daily.report'].sudo().browse(report_id)

        if not report.exists():
            return self._json_response({
                'success': False,
                'error': 'Report not found'
            }, 404)

        vals = {}

        if post.get('shooting_id'):
            shooting = request.env['sica.mobile.shooting'].sudo().browse(int(post.get('shooting_id')))
            if not shooting.exists():
                return self._json_response({
                    'success': False,
                    'error': 'Shooting not found'
                }, 404)
            vals['shooting_id'] = shooting.id

        if post.get('membership_no'):
            member = self._get_member_by_no(post.get('membership_no'))
            vals['member_id'] = member.id if member else False

        if post.get('report_date'):
            vals['report_date'] = post.get('report_date')

        if post.get('remarks') is not None:
            vals['remarks'] = post.get('remarks') or ''

        if post.get('approval_status'):
            vals['approval_status'] = post.get('approval_status')

        if post.get('approved_by_member_no'):
            approved_member = self._get_member_by_no(post.get('approved_by_member_no'))
            vals['approved_by_member_id'] = approved_member.id if approved_member else False

        if post.get('approval_remarks') is not None:
            vals['approval_remarks'] = post.get('approval_remarks') or ''

        report.write(vals)

        images = request.httprequest.files.getlist('images')

        for img in images:
            request.env['shooting.daily.report.image'].sudo().create({
                'report_id': report.id,
                'image': base64.b64encode(img.read()).decode('utf-8'),
                'image_filename': img.filename,
            })

        return self._json_response({
            'success': True,
            'message': 'Report updated successfully',
            'report': self._report_vals(report)
        })

    @http.route('/api/shootings/report/<int:report_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
    def delete_shooting_report(self, report_id, **kw):
        report = request.env['shooting.daily.report'].sudo().browse(report_id)

        if not report.exists():
            return self._json_response({
                'success': False,
                'error': 'Report not found'
            }, 404)

        report.unlink()

        return self._json_response({
            'success': True,
            'message': 'Report deleted successfully'
        })

    @http.route('/api/shootings/report/image/<int:image_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_shooting_report_image(self, image_id, **kw):
        img = request.env['shooting.daily.report.image'].sudo().browse(image_id)

        if not img.exists() or not img.image:
            return request.not_found()

        image = base64.b64decode(img.image)

        content_type = 'image/jpeg'
        filename = img.image_filename or 'report_image.jpg'

        if filename.lower().endswith('.png'):
            content_type = 'image/png'
        elif filename.lower().endswith('.webp'):
            content_type = 'image/webp'
        elif filename.lower().endswith('.gif'):
            content_type = 'image/gif'

        return request.make_response(image, headers=[
            ('Content-Type', content_type),
            ('Content-Disposition', 'inline; filename="%s"' % filename),
            ('Content-Length', str(len(image))),
        ])