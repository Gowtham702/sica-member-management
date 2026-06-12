from odoo import http, fields
from odoo.http import request, Response
import base64
import json


class MemberStatusAPI(http.Controller):

    def _json_response(self, data, status=200):
        return Response(
            json.dumps(data),
            status=status,
            content_type='application/json;charset=utf-8'
        )

    def _get_base_url(self):
        base_url = request.env['ir.config_parameter'].sudo().get_param(
            'web.base.url.image'
        ) or request.env['ir.config_parameter'].sudo().get_param(
            'web.base.url'
        ) or 'http://localhost:8059'

        return base_url.replace('0.0.0.0:8069', 'localhost:8059').rstrip('/')

    def _get_json_data(self):
        try:
            data = request.httprequest.data.decode('utf-8')
            return json.loads(data) if data else {}
        except Exception:
            return {}

    # GET ALL STATUS
    @http.route('/api/member_status', auth='public', type='http', methods=['GET'], csrf=False)
    def get_status(self, **kw):

        base_url = self._get_base_url()

        statuses = request.env['member.status'].sudo().search([
            ('expiry_time', '>=', fields.Datetime.now())
        ])

        result = []

        for rec in statuses:
            result.append({
                'id': rec.id,
                'member_id': rec.member_id.id,
                'member_name': rec.member_id.name,
                'caption': rec.caption or '',
                'media_type': rec.media_type or '',
                'media_url': '%s/get/status/media/%s' % (base_url, rec.id),
                'expiry_time': str(rec.expiry_time),
            })

        return self._json_response({"statuses": result})

    # GET STATUS BY ID
    @http.route('/api/member_status/<int:status_id>', auth='public', type='http', methods=['GET'], csrf=False)
    def get_status_by_id(self, status_id, **kw):

        base_url = self._get_base_url()

        rec = request.env['member.status'].sudo().browse(status_id)

        if not rec.exists():
            return self._json_response({"error": "Status not found"}, 404)

        result = {
            'id': rec.id,
            'member_id': rec.member_id.id,
            'member_name': rec.member_id.name,
            'caption': rec.caption or '',
            'media_type': rec.media_type or '',
            'media_url': '%s/get/status/media/%s' % (base_url, rec.id),
            'expiry_time': str(rec.expiry_time),
        }

        return self._json_response(result)

    # POST CREATE STATUS
    @http.route('/api/member_status', auth='public', type='http', methods=['POST'], csrf=False)
    def create_status(self, **kw):

        video = request.httprequest.files.get('video')

        if not video:
            return self._json_response({"error": "Video file is required"}, 400)

        member = request.env['res.member'].sudo().search([], limit=1)

        if not member:
            return self._json_response({"error": "No member found in res.member"}, 404)

        video_content = base64.b64encode(video.read()).decode('utf-8')

        status = request.env['member.status'].sudo().create({
            'member_id': member.id,
            'caption': kw.get('caption') or 'Test video status',
            'media_type': 'video',
            'media_file': video_content,
            'media_filename': video.filename,
            'expiry_time': kw.get('expiry_time') or '2026-12-31 23:59:59',
        })

        base_url = self._get_base_url()

        return self._json_response({
            "message": "Video uploaded successfully",
            "id": status.id,
            "member_id": member.id,
            "video_url": "%s/get/status/media/%s" % (base_url, status.id)
        }, 201)
    
    # PUT UPDATE STATUS BY ID
    @http.route('/api/member_status/<int:status_id>', auth='public', type='http', methods=['PUT'], csrf=False)
    def update_status(self, status_id, **kw):

        data = self._get_json_data()

        status = request.env['member.status'].sudo().browse(status_id)

        if not status.exists():
            return self._json_response({"error": "Status not found"}, 404)

        vals = {}

        if data.get('member_id'):
            member = request.env['res.member'].sudo().browse(int(data.get('member_id')))
            if not member.exists():
                return self._json_response({"error": "Member not found"}, 404)
            vals['member_id'] = member.id

        if 'caption' in data:
            vals['caption'] = data.get('caption') or ''

        if 'media_type' in data:
            vals['media_type'] = data.get('media_type') or 'image'

        if 'media_file' in data:
            vals['media_file'] = data.get('media_file')

        if 'media_filename' in data:
            vals['media_filename'] = data.get('media_filename')

        if 'expiry_time' in data:
            vals['expiry_time'] = data.get('expiry_time')

        status.write(vals)

        return self._json_response({
            "message": "Status updated successfully",
            "id": status.id
        })

    # DELETE STATUS BY ID
    @http.route('/api/member_status/<int:status_id>', auth='public', type='http', methods=['DELETE'], csrf=False)
    def delete_status(self, status_id, **kw):

        status = request.env['member.status'].sudo().browse(status_id)

        if not status.exists():
            return self._json_response({"error": "Status not found"}, 404)

        status.unlink()

        return self._json_response({
            "message": "Status deleted successfully",
            "id": status_id
        })

    # GET MEDIA FILE
    @http.route('/get/status/media/<int:status_id>', auth='public', type='http', methods=['GET'], csrf=False)
    def get_status_media(self, status_id, **kw):

        status = request.env['member.status'].sudo().browse(status_id)

        if not status.exists() or not status.media_file:
            return request.not_found()

        media = base64.b64decode(status.media_file)

        content_type = 'image/jpeg'

        if status.media_type == 'video':
            content_type = 'video/mp4'

        return request.make_response(
            media,
            headers=[
                ('Content-Type', content_type),
                ('Content-Disposition', 'inline; filename="%s"' % (
                    status.media_filename or 'status_media'
                ))
            ]
        )