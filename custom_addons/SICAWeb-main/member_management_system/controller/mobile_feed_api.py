import re
from odoo import http
from odoo.http import request, Response
import json
import base64


class MobileFeedAPI(http.Controller):

    def _json_response(self, data, status=200):
        return Response(json.dumps(data), status=status, content_type='application/json;charset=utf-8')

    def _base_url(self):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url.image') \
            or request.env['ir.config_parameter'].sudo().get_param('web.base.url') \
            or 'http://localhost:8059'
        return base_url.rstrip('/')

    def _get_member_by_no(self, membership_no):
        return request.env['res.member'].sudo().search([
            ('membership_no', '=', str(membership_no))
        ], limit=1)

    def _extract_emojis(self, text):
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "\U00002700-\U000027BF"
            "\U0001F900-\U0001F9FF"
            "]+",
            flags=re.UNICODE
        )
        return emoji_pattern.findall(text or "")

    # POSTS

    @http.route('/api/posts', type='http', auth='public', methods=['GET'], csrf=False)
    def get_posts(self, **kw):
        posts = request.env['sica.mobile.post'].sudo().search([], order='create_date desc')
        base_url = self._base_url()

        result = []
        for post in posts:
            result.append({
                'id': post.id,
                'membership_no': post.member_id.membership_no or '',
                'member_name': post.member_id.name or '',
                'text': post.text or '',
                'image_url': '%s/api/posts/image/%s' % (base_url, post.id) if post.image else '',
                'comments_count': post.comments_count,
                'share_count': post.share_count,
                'reaction_count': post.reaction_count,
                'created_date': str(post.create_date),
            })

        return self._json_response({'posts': result})

    @http.route('/api/posts/<int:post_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_post_by_id(self, post_id, **kw):
        post = request.env['sica.mobile.post'].sudo().browse(post_id)

        if not post.exists():
            return self._json_response({'error': 'Post not found'}, 404)

        base_url = self._base_url()

        return self._json_response({
            'id': post.id,
            'membership_no': post.member_id.membership_no or '',
            'member_name': post.member_id.name or '',
            'text': post.text or '',
            'image_url': '%s/api/posts/image/%s' % (base_url, post.id) if post.image else '',
            'comments_count': post.comments_count,
            'share_count': post.share_count,
            'reaction_count': post.reaction_count,
            'created_date': str(post.create_date),
        })

    @http.route(['/api/posts/create', '/api/posts/create/'], type='http', auth='public', methods=['POST'], csrf=False)
    def create_post(self, **post):
        try:
            membership_no = post.get('membership_no')
            text = post.get('text') or ''

            if not membership_no:
                return self._json_response({'success': False, 'error': 'membership_no is required'}, 400)

            member = self._get_member_by_no(membership_no)

            if not member:
                return self._json_response({'success': False, 'error': 'Member not found'}, 404)

            image_file = post.get('image')
            image_data = False
            image_filename = ''

            if image_file:
                image_data = base64.b64encode(image_file.read())
                image_filename = image_file.filename

            emojis = self._extract_emojis(text)

            record = request.env['sica.mobile.post'].sudo().create({
                'member_id': member.id,
                'text': text,
                'image': image_data,
                'image_filename': image_filename,
                'share_count': int(post.get('share_count') or 0),
                'reaction_count': int(post.get('reaction_count') or 0),
            })

            return self._json_response({
                'success': True,
                'message': 'Post created successfully',
                'id': record.id,
                'membership_no': record.member_id.membership_no or '',
                'member_name': record.member_id.name or '',
                'text': record.text or '',
                'posted_datetime': str(record.create_date),
                'share_count': record.share_count,
                'reaction_count': record.reaction_count,
                'emojis_available': True if emojis else False,
                'emoji_count': len(emojis),
                'emojis': emojis,
            })

        except Exception as e:
            return self._json_response({'success': False, 'error': str(e)}, 500)

    @http.route('/api/posts/<int:post_id>', type='http', auth='public', methods=['PUT', 'POST'], csrf=False)
    def update_post(self, post_id, **post):
        rec = request.env['sica.mobile.post'].sudo().browse(post_id)

        if not rec.exists():
            return self._json_response({'error': 'Post not found'}, 404)

        vals = {}

        if post.get('membership_no'):
            member = self._get_member_by_no(post.get('membership_no'))
            if not member:
                return self._json_response({'error': 'Member not found'}, 404)
            vals['member_id'] = member.id

        if post.get('text') is not None:
            vals['text'] = post.get('text')

        if post.get('share_count'):
            vals['share_count'] = int(post.get('share_count'))

        if post.get('reaction_count'):
            vals['reaction_count'] = int(post.get('reaction_count'))

        image_file = post.get('image')
        if image_file:
            vals['image'] = base64.b64encode(image_file.read())
            vals['image_filename'] = image_file.filename

        rec.write(vals)

        return self._json_response({
            'success': True,
            'message': 'Post updated successfully',
            'post_id': rec.id
        })

    @http.route('/api/posts/<int:post_id>', type='http', auth='public', methods=['DELETE', 'POST'], csrf=False)
    def delete_post(self, post_id, **kw):
        rec = request.env['sica.mobile.post'].sudo().browse(post_id)

        if not rec.exists():
            return self._json_response({'error': 'Post not found'}, 404)

        rec.unlink()

        return self._json_response({'success': True, 'message': 'Post deleted successfully'})

    @http.route('/api/posts/image/<int:post_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_post_image(self, post_id, **kw):
        post = request.env['sica.mobile.post'].sudo().browse(post_id)

        if not post.exists() or not post.image:
            return request.not_found()

        image = base64.b64decode(post.image)

        return request.make_response(
            image,
            headers=[
                ('Content-Type', 'image/jpeg'),
                ('Content-Disposition', 'inline')
            ]
        )

    # SHOOTING

    @http.route('/api/shootings', type='http', auth='public', methods=['GET'], csrf=False)
    def get_shootings(self, **kw):
        shootings = request.env['sica.mobile.shooting'].sudo().search([], order='create_date desc')
        base_url = self._base_url()

        result = []
        for shoot in shootings:
            result.append({
                'id': shoot.id,
                'title': shoot.title or '',
                'description': shoot.description or '',
                'location': shoot.location or '',
                'production_house': shoot.production_house or '',
                'from_date': str(shoot.from_date) if shoot.from_date else '',
                'to_date': str(shoot.to_date) if shoot.to_date else '',
                'status': shoot.status,
                'team_members': [
                    {
                        'membership_no': m.membership_no or '',
                        'name': m.name or '',
                    }
                    for m in shoot.team_member_ids
                ],
                'team_members_count': len(shoot.team_member_ids),
                'image_url': '%s/api/shootings/image/%s' % (base_url, shoot.id) if shoot.image else '',
            })

        return self._json_response({'shootings': result})

    @http.route('/api/shootings/<int:shoot_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_shooting_by_id(self, shoot_id, **kw):
        shoot = request.env['sica.mobile.shooting'].sudo().browse(shoot_id)

        if not shoot.exists():
            return self._json_response({'error': 'Shooting not found'}, 404)

        base_url = self._base_url()

        return self._json_response({
            'id': shoot.id,
            'title': shoot.title or '',
            'description': shoot.description or '',
            'location': shoot.location or '',
            'production_house': shoot.production_house or '',
            'from_date': str(shoot.from_date) if shoot.from_date else '',
            'to_date': str(shoot.to_date) if shoot.to_date else '',
            'status': shoot.status,
            'team_members': [
                {
                    'membership_no': m.membership_no or '',
                    'name': m.name or '',
                }
                for m in shoot.team_member_ids
            ],
            'team_members_count': len(shoot.team_member_ids),
            'image_url': '%s/api/shootings/image/%s' % (base_url, shoot.id) if shoot.image else '',
        })

    @http.route('/api/shootings', type='http', auth='public', methods=['POST'], csrf=False)
    def create_shooting(self, **post):
        image_file = post.get('image')

        team_ids = []
        if post.get('team_membership_nos'):
            membership_nos = [x.strip() for x in post.get('team_membership_nos').split(',') if x.strip()]
            members = request.env['res.member'].sudo().search([
                ('membership_no', 'in', membership_nos)
            ])
            team_ids = members.ids

        vals = {
            'title': post.get('title') or '',
            'description': post.get('description') or '',
            'location': post.get('location') or '',
            'production_house': post.get('production_house') or '',
            'from_date': post.get('from_date') or False,
            'to_date': post.get('to_date') or False,
            'status': post.get('status') or 'pre_production',
            'team_member_ids': [(6, 0, team_ids)],
        }

        if image_file:
            vals['image'] = base64.b64encode(image_file.read())
            vals['image_filename'] = image_file.filename

        rec = request.env['sica.mobile.shooting'].sudo().create(vals)

        return self._json_response({
            'success': True,
            'message': 'Shooting created successfully',
            'shooting_id': rec.id
        })

    @http.route('/api/shootings/<int:shoot_id>', type='http', auth='public', methods=['PUT', 'POST'], csrf=False)
    def update_shooting(self, shoot_id, **post):
        rec = request.env['sica.mobile.shooting'].sudo().browse(shoot_id)

        if not rec.exists():
            return self._json_response({'error': 'Shooting not found'}, 404)

        vals = {}

        for field in ['title', 'description', 'location', 'production_house', 'from_date', 'to_date', 'status']:
            if post.get(field):
                vals[field] = post.get(field)

        if post.get('team_membership_nos'):
            membership_nos = [x.strip() for x in post.get('team_membership_nos').split(',') if x.strip()]
            members = request.env['res.member'].sudo().search([
                ('membership_no', 'in', membership_nos)
            ])
            vals['team_member_ids'] = [(6, 0, members.ids)]

        image_file = post.get('image')
        if image_file:
            vals['image'] = base64.b64encode(image_file.read())
            vals['image_filename'] = image_file.filename

        rec.write(vals)

        return self._json_response({
            'success': True,
            'message': 'Shooting updated successfully',
            'shooting_id': rec.id
        })

    @http.route('/api/shootings/<int:shoot_id>', type='http', auth='public', methods=['DELETE', 'POST'], csrf=False)
    def delete_shooting(self, shoot_id, **kw):
        rec = request.env['sica.mobile.shooting'].sudo().browse(shoot_id)

        if not rec.exists():
            return self._json_response({'error': 'Shooting not found'}, 404)

        rec.unlink()

        return self._json_response({'success': True, 'message': 'Shooting deleted successfully'})

    @http.route('/api/shootings/image/<int:shoot_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_shooting_image(self, shoot_id, **kw):
        shoot = request.env['sica.mobile.shooting'].sudo().browse(shoot_id)

        if not shoot.exists() or not shoot.image:
            return request.not_found()

        image = base64.b64decode(shoot.image)

        return request.make_response(
            image,
            headers=[
                ('Content-Type', 'image/jpeg'),
                ('Content-Disposition', 'inline')
            ]
        )

    # REQUIREMENTS

    @http.route('/api/requirements', type='http', auth='public', methods=['GET'], csrf=False)
    def get_requirements(self, **kw):
        requirements = request.env['sica.mobile.requirement'].sudo().search([], order='create_date desc')

        result = []
        for req in requirements:
            result.append({
                'id': req.id,
                'membership_no': req.member_id.membership_no or '',
                'member_name': req.member_id.name or '',
                'requirement_type': req.requirement_type,
                'title': req.title,
                'description': req.description or '',
                'location': req.location or '',
                'event_date': str(req.event_date) if req.event_date else '',
                'experience': req.experience or '',
                'created_date': str(req.create_date),
            })

        return self._json_response({'requirements': result})

    @http.route('/api/requirements/<int:req_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_requirement_by_id(self, req_id, **kw):
        req = request.env['sica.mobile.requirement'].sudo().browse(req_id)

        if not req.exists():
            return self._json_response({'error': 'Requirement not found'}, 404)

        return self._json_response({
            'id': req.id,
            'membership_no': req.member_id.membership_no or '',
            'member_name': req.member_id.name or '',
            'requirement_type': req.requirement_type,
            'title': req.title,
            'description': req.description or '',
            'location': req.location or '',
            'event_date': str(req.event_date) if req.event_date else '',
            'experience': req.experience or '',
            'created_date': str(req.create_date),
        })

    @http.route('/api/requirements', type='http', auth='public', methods=['POST'], csrf=False)
    def create_requirement(self, **post):
        membership_no = post.get('membership_no')

        if not membership_no:
            return self._json_response({'error': 'membership_no is required'}, 400)

        member = self._get_member_by_no(membership_no)

        if not member:
            return self._json_response({'error': 'Member not found'}, 404)

        rec = request.env['sica.mobile.requirement'].sudo().create({
            'member_id': member.id,
            'requirement_type': post.get('requirement_type') or 'job_post',
            'title': post.get('title') or '',
            'description': post.get('description') or '',
            'location': post.get('location') or '',
            'event_date': post.get('event_date') or False,
            'experience': post.get('experience') or '',
        })

        return self._json_response({
            'success': True,
            'message': 'Requirement created successfully',
            'requirement_id': rec.id
        })

    @http.route('/api/requirements/<int:req_id>', type='http', auth='public', methods=['PUT', 'POST'], csrf=False)
    def update_requirement(self, req_id, **post):
        rec = request.env['sica.mobile.requirement'].sudo().browse(req_id)

        if not rec.exists():
            return self._json_response({'error': 'Requirement not found'}, 404)

        vals = {}

        if post.get('membership_no'):
            member = self._get_member_by_no(post.get('membership_no'))
            if not member:
                return self._json_response({'error': 'Member not found'}, 404)
            vals['member_id'] = member.id

        for field in ['requirement_type', 'title', 'description', 'location', 'event_date', 'experience']:
            if post.get(field):
                vals[field] = post.get(field)

        rec.write(vals)

        return self._json_response({
            'success': True,
            'message': 'Requirement updated successfully',
            'requirement_id': rec.id
        })

    @http.route('/api/requirements/<int:req_id>', type='http', auth='public', methods=['DELETE', 'POST'], csrf=False)
    def delete_requirement(self, req_id, **kw):
        rec = request.env['sica.mobile.requirement'].sudo().browse(req_id)

        if not rec.exists():
            return self._json_response({'error': 'Requirement not found'}, 404)

        rec.unlink()

        return self._json_response({'success': True, 'message': 'Requirement deleted successfully'})

    # MEMBER BASED FAST APIs USING MEMBERSHIP NO

    @http.route('/api/member/dashboard/<string:membership_no>', type='http', auth='public', methods=['GET'], csrf=False)
    def member_dashboard(self, membership_no, **kw):
        base_url = self._base_url()
        offset = int(kw.get('offset') or 0)
        limit = int(kw.get('limit') or 10)

        member = self._get_member_by_no(membership_no)

        if not member:
            return self._json_response({'success': False, 'error': 'Member not found'}, 404)

        member_id = member.id

        posts = request.env['sica.mobile.post'].sudo().search(
            [('member_id', '=', member_id)],
            offset=offset,
            limit=limit,
            order='create_date desc'
        )

        post_vals = []
        for post in posts:
            emojis = self._extract_emojis(post.text or '')
            post_vals.append({
                'id': post.id,
                'text': post.text or '',
                'image_url': '%s/api/posts/image/%s' % (base_url, post.id) if post.image else '',
                'comments_count': post.comments_count,
                'share_count': post.share_count,
                'reaction_count': post.reaction_count,
                'emoji_count': len(emojis),
                'emojis': emojis,
                'created_date': str(post.create_date),
            })

        shootings = request.env['sica.mobile.shooting'].sudo().search(
            [('team_member_ids', 'in', [member_id])],
            offset=offset,
            limit=limit,
            order='create_date desc'
        )

        shooting_vals = []
        for shoot in shootings:
            shooting_vals.append({
                'id': shoot.id,
                'title': shoot.title or '',
                'description': shoot.description or '',
                'location': shoot.location or '',
                'production_house': shoot.production_house or '',
                'from_date': str(shoot.from_date) if shoot.from_date else '',
                'to_date': str(shoot.to_date) if shoot.to_date else '',
                'status': shoot.status or '',
                'team_members_count': len(shoot.team_member_ids),
                'image_url': '%s/api/shootings/image/%s' % (base_url, shoot.id) if shoot.image else '',
            })

        requirements = request.env['sica.mobile.requirement'].sudo().search(
            [('member_id', '=', member_id)],
            offset=offset,
            limit=limit,
            order='create_date desc'
        )

        requirement_vals = []
        for req in requirements:
            requirement_vals.append({
                'id': req.id,
                'requirement_type': req.requirement_type or '',
                'title': req.title or '',
                'description': req.description or '',
                'location': req.location or '',
                'event_date': str(req.event_date) if req.event_date else '',
                'experience': req.experience or '',
                'created_date': str(req.create_date),
            })

        return self._json_response({
            'success': True,
            'member': {
                'membership_no': member.membership_no or '',
                'name': member.name or '',
                'designation': member.designation or '',
                'grade': member.grade or '',
                'state': member.state or '',
                'mobile_number': member.contact1 or '',
                'email': member.email or '',
            },
            'posts': post_vals,
            'shootings': shooting_vals,
            'requirements': requirement_vals,
            'counts': {
                'posts': request.env['sica.mobile.post'].sudo().search_count([('member_id', '=', member_id)]),
                'shootings': request.env['sica.mobile.shooting'].sudo().search_count([('team_member_ids', 'in', [member_id])]),
                'requirements': request.env['sica.mobile.requirement'].sudo().search_count([('member_id', '=', member_id)]),
            }
        })