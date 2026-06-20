import re
import json
import base64
from odoo import http, fields
from odoo.http import request, Response


class MobileFeedAPI(http.Controller):

    def _json_response(self, data, status=200):
        return Response(json.dumps(data), status=status, content_type='application/json;charset=utf-8')

    def _base_url(self):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url.image') or \
                   request.env['ir.config_parameter'].sudo().get_param('web.base.url') or \
                   'http://localhost:8059'
        return base_url.rstrip('/')

    def _get_member_by_no(self, membership_no):
        if not membership_no:
            return request.env['res.member'].sudo()

        membership_no = str(membership_no).strip()

        member = request.env['res.member'].sudo().search([
            ('membership_no', '=', membership_no)
        ], limit=1)

        if not member and membership_no.isdigit():
            member = request.env['res.member'].sudo().search([
                ('membership_no', '=', str(int(membership_no)))
            ], limit=1)

        if not member and membership_no.isdigit():
            member = request.env['res.member'].sudo().search([
                ('membership_no', '=', membership_no.zfill(4))
            ], limit=1)

        return member

    def _member_image(self, member):
        if member and member.image_1920:
            return '%s/get/public/image/res.member/%s/image_1920' % (self._base_url(), member.id)
        return ''

    def _extract_emojis(self, text):
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "\U00002700-\U000027BF"
            "\U0001F900-\U0001F9FF"
            "\U0001FA00-\U0001FAFF"
            "]+",
            flags=re.UNICODE
        )
        return emoji_pattern.findall(text or "")

    def _post_vals(self, post):
        base_url = self._base_url()
        emojis = self._extract_emojis(post.text or '')
        return {
            'id': post.id,
            'membership_no': post.member_id.membership_no or '',
            'member_name': post.member_id.name or '',
            'member_image': self._member_image(post.member_id),
            'text': post.text or '',
            'image_url': '%s/api/posts/image/%s' % (base_url, post.id) if post.image else '',
            'comments_count': post.comments_count,
            'share_count': post.share_count,
            'reaction_count': post.reaction_count,
            'emoji_count': len(emojis),
            'emojis': emojis,
            'created_date': str(post.create_date),
        }

    def _shooting_vals(self, shoot):
        base_url = self._base_url()
        return {
            'id': shoot.id,
            'membership_no': shoot.member_id.membership_no if shoot.member_id else '',
            'member_name': shoot.member_id.name if shoot.member_id else '',
            'title': shoot.title or '',
            'description': shoot.description or '',
            'location': shoot.location or '',
            'production_house': shoot.production_house or '',
            'from_date': str(shoot.from_date) if shoot.from_date else '',
            'to_date': str(shoot.to_date) if shoot.to_date else '',
            'status': shoot.status or '',
            'team_members': [{
                'membership_no': m.membership_no or '',
                'name': m.name or '',
                'image': self._member_image(m),
            } for m in shoot.team_member_ids],
            'team_members_count': len(shoot.team_member_ids),
            'image_url': self._member_image(shoot.member_id) if shoot.member_id else '',
            'movie_poster_url': self._member_image(shoot.member_id) if shoot.member_id else '',
            'created_date': str(shoot.create_date),
        }

    def _requirement_vals(self, req):
        return {
            'id': req.id,
            'membership_no': req.member_id.membership_no or '',
            'member_name': req.member_id.name or '',
            'member_image': self._member_image(req.member_id),
            'requirement_type': req.requirement_type or '',
            'title': req.title or '',
            'description': req.description or '',
            'location': req.location or '',
            'event_date': str(req.event_date) if req.event_date else '',
            'experience': req.experience or '',
            'created_date': str(req.create_date),
        }

    # POSTS

    @http.route('/api/posts', type='http', auth='public', methods=['GET'], csrf=False)
    def get_posts(self, **kw):
        offset = int(kw.get('offset') or 0)
        limit = int(kw.get('limit') or 20)
        posts = request.env['sica.mobile.post'].sudo().search([], offset=offset, limit=limit, order='create_date desc')
        return self._json_response({'success': True, 'posts': [self._post_vals(p) for p in posts]})

    @http.route('/api/posts/<int:post_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_post_by_id(self, post_id, **kw):
        post = request.env['sica.mobile.post'].sudo().browse(post_id)
        if not post.exists():
            return self._json_response({'success': False, 'error': 'Post not found'}, 404)

        comments = request.env['sica.mobile.comment'].sudo().search([('post_id', '=', post.id)], order='create_date asc')
        data = self._post_vals(post)
        data['comments'] = [{
            'id': c.id,
            'membership_no': c.member_id.membership_no or '',
            'member_name': c.member_id.name or '',
            'member_image': self._member_image(c.member_id),
            'comment': c.comment or '',
            'created_date': str(c.create_date),
        } for c in comments]
        return self._json_response({'success': True, 'post': data})

    @http.route(['/api/posts/create', '/api/posts/create/'], type='http', auth='public', methods=['POST'], csrf=False)
    def create_post(self, **post):
        membership_no = post.get('membership_no')
        member = self._get_member_by_no(membership_no)
        if not member:
            return self._json_response({'success': False, 'error': 'Member not found'}, 404)

        image_file = post.get('image')
        image_data = False
        image_filename = ''
        if image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
            image_filename = image_file.filename

        rec = request.env['sica.mobile.post'].sudo().create({
            'member_id': member.id,
            'text': post.get('text') or '',
            'image': image_data,
            'image_filename': image_filename,
            'share_count': int(post.get('share_count') or 0),
            'reaction_count': int(post.get('reaction_count') or 0),
        })

        return self._json_response({
            'success': True,
            'message': 'Post created successfully',
            'post': self._post_vals(rec)
        }, 201)

    @http.route('/api/posts/<int:post_id>', type='http', auth='public', methods=['PUT', 'POST'], csrf=False)
    def update_post(self, post_id, **post):
        rec = request.env['sica.mobile.post'].sudo().browse(post_id)
        if not rec.exists():
            return self._json_response({'success': False, 'error': 'Post not found'}, 404)

        vals = {}

        if post.get('membership_no'):
            member = self._get_member_by_no(post.get('membership_no'))
            if not member:
                return self._json_response({'success': False, 'error': 'Member not found'}, 404)
            vals['member_id'] = member.id

        if post.get('text') is not None:
            vals['text'] = post.get('text')

        if post.get('share_count') is not None:
            vals['share_count'] = int(post.get('share_count') or 0)

        if post.get('reaction_count') is not None:
            vals['reaction_count'] = int(post.get('reaction_count') or 0)

        image_file = post.get('image')
        if image_file:
            vals['image'] = base64.b64encode(image_file.read()).decode('utf-8')
            vals['image_filename'] = image_file.filename

        rec.write(vals)
        return self._json_response({'success': True, 'message': 'Post updated successfully', 'post': self._post_vals(rec)})

    @http.route('/api/posts/<int:post_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
    def delete_post(self, post_id, **kw):
        rec = request.env['sica.mobile.post'].sudo().browse(post_id)
        if not rec.exists():
            return self._json_response({'success': False, 'error': 'Post not found'}, 404)
        rec.unlink()
        return self._json_response({'success': True, 'message': 'Post deleted successfully'})

    @http.route('/api/posts/image/<int:post_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_post_image(self, post_id, **kw):
        post = request.env['sica.mobile.post'].sudo().browse(post_id)
        if not post.exists() or not post.image:
            return request.not_found()

        image = base64.b64decode(post.image)
        content_type = 'image/jpeg'

        if post.image_filename:
            filename = post.image_filename.lower()
            if filename.endswith('.png'):
                content_type = 'image/png'
            elif filename.endswith('.webp'):
                content_type = 'image/webp'
            elif filename.endswith('.gif'):
                content_type = 'image/gif'

        return request.make_response(image, headers=[
            ('Content-Type', content_type),
            ('Content-Disposition', 'inline; filename="%s"' % (post.image_filename or 'post_image')),
            ('Content-Length', str(len(image))),
        ])

    # POST ACTIONS

    @http.route('/api/posts/like', type='http', auth='public', methods=['POST'], csrf=False)
    def like_post(self, **post):
        member = self._get_member_by_no(post.get('membership_no'))
        post_rec = request.env['sica.mobile.post'].sudo().browse(int(post.get('post_id') or 0))

        if not member or not post_rec.exists():
            return self._json_response({'success': False, 'error': 'Invalid member or post'}, 400)

        reaction_type = post.get('reaction') or 'like'

        old = request.env['sica.mobile.reaction'].sudo().search([
            ('post_id', '=', post_rec.id),
            ('member_id', '=', member.id)
        ], limit=1)

        if old:
            old.write({'reaction': reaction_type})
        else:
            request.env['sica.mobile.reaction'].sudo().create({
                'post_id': post_rec.id,
                'member_id': member.id,
                'reaction': reaction_type,
            })

        post_rec.write({
            'reaction_count': request.env['sica.mobile.reaction'].sudo().search_count([('post_id', '=', post_rec.id)])
        })

        return self._json_response({'success': True, 'reaction_count': post_rec.reaction_count})

    @http.route('/api/posts/unlike', type='http', auth='public', methods=['POST'], csrf=False)
    def unlike_post(self, **post):
        member = self._get_member_by_no(post.get('membership_no'))
        post_rec = request.env['sica.mobile.post'].sudo().browse(int(post.get('post_id') or 0))

        if not member or not post_rec.exists():
            return self._json_response({'success': False, 'error': 'Invalid member or post'}, 400)

        reaction = request.env['sica.mobile.reaction'].sudo().search([
            ('post_id', '=', post_rec.id),
            ('member_id', '=', member.id)
        ], limit=1)

        if reaction:
            reaction.unlink()

        post_rec.write({
            'reaction_count': request.env['sica.mobile.reaction'].sudo().search_count([('post_id', '=', post_rec.id)])
        })

        return self._json_response({'success': True, 'reaction_count': post_rec.reaction_count})

    @http.route('/api/comments/create', type='http', auth='public', methods=['POST'], csrf=False)
    def create_comment(self, **post):
        member = self._get_member_by_no(post.get('membership_no'))
        post_rec = request.env['sica.mobile.post'].sudo().browse(int(post.get('post_id') or 0))
        comment_text = post.get('comment') or ''

        if not member or not post_rec.exists() or not comment_text:
            return self._json_response({'success': False, 'error': 'Invalid data'}, 400)

        comment = request.env['sica.mobile.comment'].sudo().create({
            'post_id': post_rec.id,
            'member_id': member.id,
            'comment': comment_text,
        })

        post_rec.write({
            'comments_count': request.env['sica.mobile.comment'].sudo().search_count([('post_id', '=', post_rec.id)])
        })

        return self._json_response({
            'success': True,
            'comment_id': comment.id,
            'comments_count': post_rec.comments_count
        }, 201)

    @http.route('/api/comments/<int:post_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_comments(self, post_id, **kw):
        comments = request.env['sica.mobile.comment'].sudo().search([('post_id', '=', post_id)], order='create_date asc')
        return self._json_response({
            'success': True,
            'comments': [{
                'id': c.id,
                'membership_no': c.member_id.membership_no or '',
                'member_name': c.member_id.name or '',
                'member_image': self._member_image(c.member_id),
                'comment': c.comment or '',
                'created_date': str(c.create_date),
            } for c in comments]
        })

    # FOLLOW

    @http.route('/api/follow', type='http', auth='public', methods=['POST'], csrf=False)
    def follow_user(self, **post):
        follower = self._get_member_by_no(post.get('membership_no'))
        following = self._get_member_by_no(post.get('following_membership_no'))

        if not follower or not following:
            return self._json_response({'success': False, 'error': 'Member not found'}, 404)

        if follower.id == following.id:
            return self._json_response({'success': False, 'error': 'Cannot follow yourself'}, 400)

        old = request.env['sica.mobile.follow'].sudo().search([
            ('follower_id', '=', follower.id),
            ('following_id', '=', following.id),
        ], limit=1)

        if not old:
            request.env['sica.mobile.follow'].sudo().create({
                'follower_id': follower.id,
                'following_id': following.id,
            })

        return self._json_response({'success': True, 'message': 'Followed successfully'})

    @http.route('/api/unfollow', type='http', auth='public', methods=['POST'], csrf=False)
    def unfollow_user(self, **post):
        follower = self._get_member_by_no(post.get('membership_no'))
        following = self._get_member_by_no(post.get('following_membership_no'))

        if not follower or not following:
            return self._json_response({'success': False, 'error': 'Member not found'}, 404)

        rec = request.env['sica.mobile.follow'].sudo().search([
            ('follower_id', '=', follower.id),
            ('following_id', '=', following.id),
        ], limit=1)

        if rec:
            rec.unlink()

        return self._json_response({'success': True, 'message': 'Unfollowed successfully'})

    # SHOOTING

    @http.route('/api/shootings', type='http', auth='public', methods=['GET'], csrf=False)
    def get_shootings(self, **kw):
        offset = int(kw.get('offset') or 0)
        limit = int(kw.get('limit') or 20)
        shootings = request.env['sica.mobile.shooting'].sudo().search([], offset=offset, limit=limit, order='create_date desc')
        return self._json_response({'success': True, 'shootings': [self._shooting_vals(s) for s in shootings]})

    @http.route('/api/shootings/<int:shoot_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_shooting_by_id(self, shoot_id, **kw):
        shoot = request.env['sica.mobile.shooting'].sudo().browse(shoot_id)
        if not shoot.exists():
            return self._json_response({'success': False, 'error': 'Shooting not found'}, 404)
        return self._json_response({'success': True, 'shooting': self._shooting_vals(shoot)})

    @http.route('/api/shootings', type='http', auth='public', methods=['POST'], csrf=False)
    def create_shooting(self, **post):
        member = self._get_member_by_no(post.get('membership_no'))

        team_ids = []
        if post.get('team_membership_nos'):
            membership_nos = [x.strip().zfill(4) for x in post.get('team_membership_nos').split(',') if x.strip()]
            team_ids = request.env['res.member'].sudo().search([('membership_no', 'in', membership_nos)]).ids

        vals = {
            'member_id': member.id if member else False,
            'title': post.get('title') or '',
            'description': post.get('description') or '',
            'location': post.get('location') or '',
            'production_house': post.get('production_house') or '',
            'from_date': post.get('from_date') or False,
            'to_date': post.get('to_date') or False,
            'status': post.get('status') or 'pre_production',
            'team_member_ids': [(6, 0, team_ids)],
        }

        image_file = post.get('image')
        if image_file:
            vals['image'] = base64.b64encode(image_file.read()).decode('utf-8')
            vals['image_filename'] = image_file.filename

        poster_file = post.get('movie_poster')
        if poster_file:
            vals['movie_poster'] = base64.b64encode(poster_file.read()).decode('utf-8')
            vals['movie_poster_filename'] = poster_file.filename

        rec = request.env['sica.mobile.shooting'].sudo().create(vals)
        return self._json_response({'success': True, 'message': 'Shooting created successfully', 'shooting': self._shooting_vals(rec)}, 201)

    @http.route('/api/shootings/<int:shoot_id>', type='http', auth='public', methods=['PUT'], csrf=False)
    def update_shooting_put(self, shoot_id, **kw):
        rec = request.env['sica.mobile.shooting'].sudo().browse(shoot_id)

        if not rec.exists():
            return self._json_response({'success': False, 'error': 'Shooting not found'}, 404)

        vals = {}

        if kw.get('membership_no'):
            member = self._get_member_by_no(kw.get('membership_no'))
            vals['member_id'] = member.id if member else False

        if kw.get('team_membership_nos'):
            membership_nos = [x.strip().zfill(4) for x in kw.get('team_membership_nos').split(',') if x.strip()]
            members = request.env['res.member'].sudo().search([('membership_no', 'in', membership_nos)])
            vals['team_member_ids'] = [(6, 0, members.ids)]

        for field in ['title', 'description', 'location', 'production_house', 'from_date', 'to_date', 'status']:
            if kw.get(field):
                vals[field] = kw.get(field)

        rec.write(vals)

        return self._json_response({
            'success': True,
            'message': 'Shooting updated successfully',
            'shooting': self._shooting_vals(rec)
        })

    @http.route('/api/shootings/<int:shoot_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
    def delete_shooting(self, shoot_id, **kw):
        rec = request.env['sica.mobile.shooting'].sudo().browse(shoot_id)
        if not rec.exists():
            return self._json_response({'success': False, 'error': 'Shooting not found'}, 404)
        rec.unlink()
        return self._json_response({'success': True, 'message': 'Shooting deleted successfully'})

    @http.route('/api/shootings/image/<int:shoot_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_shooting_image(self, shoot_id, **kw):
        shoot = request.env['sica.mobile.shooting'].sudo().browse(shoot_id)
        if not shoot.exists() or not shoot.image:
            return request.not_found()
        image = base64.b64decode(shoot.image)
        return request.make_response(image, headers=[
            ('Content-Type', 'image/jpeg'),
            ('Content-Disposition', 'inline'),
            ('Content-Length', str(len(image))),
        ])

    @http.route('/api/shootings/poster/<int:shoot_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_movie_poster(self, shoot_id, **kw):
        shoot = request.env['sica.mobile.shooting'].sudo().browse(shoot_id)
        if not shoot.exists() or not shoot.movie_poster:
            return request.not_found()
        image = base64.b64decode(shoot.movie_poster)
        return request.make_response(image, headers=[
            ('Content-Type', 'image/jpeg'),
            ('Content-Disposition', 'inline; filename="%s"' % (shoot.movie_poster_filename or 'movie_poster')),
            ('Content-Length', str(len(image))),
        ])

    # REQUIREMENTS

    @http.route('/api/requirements', type='http', auth='public', methods=['GET'], csrf=False)
    def get_requirements(self, **kw):
        offset = int(kw.get('offset') or 0)
        limit = int(kw.get('limit') or 20)
        requirements = request.env['sica.mobile.requirement'].sudo().search([], offset=offset, limit=limit, order='create_date desc')
        return self._json_response({'success': True, 'requirements': [self._requirement_vals(r) for r in requirements]})

    @http.route('/api/requirements/<int:req_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_requirement_by_id(self, req_id, **kw):
        req = request.env['sica.mobile.requirement'].sudo().browse(req_id)
        if not req.exists():
            return self._json_response({'success': False, 'error': 'Requirement not found'}, 404)
        return self._json_response({'success': True, 'requirement': self._requirement_vals(req)})

    @http.route('/api/requirements', type='http', auth='public', methods=['POST'], csrf=False)
    def create_requirement(self, **post):
        member = self._get_member_by_no(post.get('membership_no'))
        if not member:
            return self._json_response({'success': False, 'error': 'Member not found'}, 404)

        rec = request.env['sica.mobile.requirement'].sudo().create({
            'member_id': member.id,
            'requirement_type': post.get('requirement_type') or 'job_post',
            'title': post.get('title') or '',
            'description': post.get('description') or '',
            'location': post.get('location') or '',
            'event_date': post.get('event_date') or False,
            'experience': post.get('experience') or '',
        })

        return self._json_response({'success': True, 'message': 'Requirement created successfully', 'requirement': self._requirement_vals(rec)}, 201)

    @http.route('/api/requirements/<int:req_id>', type='http', auth='public', methods=['PUT', 'POST'], csrf=False)
    def update_requirement(self, req_id, **post):
        rec = request.env['sica.mobile.requirement'].sudo().browse(req_id)
        if not rec.exists():
            return self._json_response({'success': False, 'error': 'Requirement not found'}, 404)

        vals = {}

        if post.get('membership_no'):
            member = self._get_member_by_no(post.get('membership_no'))
            if not member:
                return self._json_response({'success': False, 'error': 'Member not found'}, 404)
            vals['member_id'] = member.id

        for field in ['requirement_type', 'title', 'description', 'location', 'event_date', 'experience']:
            if post.get(field):
                vals[field] = post.get(field)

        rec.write(vals)
        return self._json_response({'success': True, 'message': 'Requirement updated successfully', 'requirement': self._requirement_vals(rec)})

    @http.route('/api/requirements/<int:req_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
    def delete_requirement(self, req_id, **kw):
        rec = request.env['sica.mobile.requirement'].sudo().browse(req_id)
        if not rec.exists():
            return self._json_response({'success': False, 'error': 'Requirement not found'}, 404)
        rec.unlink()
        return self._json_response({'success': True, 'message': 'Requirement deleted successfully'})

    # FAST SCREEN APIs

    @http.route('/api/member/dashboard/<string:membership_no>', type='http', auth='public', methods=['GET'], csrf=False)
    def member_dashboard(self, membership_no, **kw):
        member = self._get_member_by_no(membership_no)
        if not member:
            return self._json_response({'success': False, 'error': 'Member not found'}, 404)

        posts = request.env['sica.mobile.post'].sudo().search([('member_id', '=', member.id)], limit=10, order='create_date desc')
        shootings = request.env['sica.mobile.shooting'].sudo().search([('team_member_ids', 'in', [member.id])], limit=10, order='create_date desc')
        requirements = request.env['sica.mobile.requirement'].sudo().search([('member_id', '=', member.id)], limit=10, order='create_date desc')

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
                'member_image': self._member_image(member),
            },
            'posts': [self._post_vals(p) for p in posts],
            'shootings': [self._shooting_vals(s) for s in shootings],
            'requirements': [self._requirement_vals(r) for r in requirements],
            'counts': {
                'posts': request.env['sica.mobile.post'].sudo().search_count([('member_id', '=', member.id)]),
                'shootings': request.env['sica.mobile.shooting'].sudo().search_count([('team_member_ids', 'in', [member.id])]),
                'requirements': request.env['sica.mobile.requirement'].sudo().search_count([('member_id', '=', member.id)]),
            }
        })

    @http.route('/api/member/posts/<string:membership_no>', type='http', auth='public', methods=['GET'], csrf=False)
    def member_posts(self, membership_no, **kw):
        member = self._get_member_by_no(membership_no)
        if not member:
            return self._json_response({'success': False, 'error': 'Member not found'}, 404)
        posts = request.env['sica.mobile.post'].sudo().search([('member_id', '=', member.id)], order='create_date desc')
        return self._json_response({'success': True, 'posts': [self._post_vals(p) for p in posts]})

    @http.route('/api/member/shootings/<string:membership_no>', type='http', auth='public', methods=['GET'], csrf=False)
    def member_shootings(self, membership_no, **kw):
        member = self._get_member_by_no(membership_no)
        if not member:
            return self._json_response({'success': False, 'error': 'Member not found'}, 404)
        shoots = request.env['sica.mobile.shooting'].sudo().search([('team_member_ids', 'in', [member.id])], order='create_date desc')
        return self._json_response({'success': True, 'shootings': [self._shooting_vals(s) for s in shoots]})

    @http.route('/api/member/requirements/<string:membership_no>', type='http', auth='public', methods=['GET'], csrf=False)
    def member_requirements(self, membership_no, **kw):
        member = self._get_member_by_no(membership_no)
        if not member:
            return self._json_response({'success': False, 'error': 'Member not found'}, 404)
        reqs = request.env['sica.mobile.requirement'].sudo().search([('member_id', '=', member.id)], order='create_date desc')
        return self._json_response({'success': True, 'requirements': [self._requirement_vals(r) for r in reqs]})

    @http.route('/api/explore', type='http', auth='public', methods=['GET'], csrf=False)
    def explore_feed(self, **kw):
        limit = int(kw.get('limit') or 10)
        posts = request.env['sica.mobile.post'].sudo().search([], limit=limit, order='create_date desc')
        shootings = request.env['sica.mobile.shooting'].sudo().search([], limit=limit, order='create_date desc')
        requirements = request.env['sica.mobile.requirement'].sudo().search([], limit=limit, order='create_date desc')

        return self._json_response({
            'success': True,
            'posts': [self._post_vals(p) for p in posts],
            'shootings': [self._shooting_vals(s) for s in shootings],
            'requirements': [self._requirement_vals(r) for r in requirements],
        })
        # ---------------------------------------------------------
    # POST ACTION API
    # ---------------------------------------------------------

    @http.route('/api/post/action', type='http', auth='public', methods=['POST'], csrf=False)
    def post_action(self, **post):
        member = self._get_member_by_no(post.get('membership_no'))
        post_rec = request.env['sica.mobile.post'].sudo().browse(int(post.get('post_id') or 0))

        if not member:
            return self._json_response({'success': False, 'error': 'Member not found'}, 404)

        if not post_rec.exists():
            return self._json_response({'success': False, 'error': 'Post not found'}, 404)

        action_type = post.get('action_type') or 'like'

        old = request.env['sica.mobile.post.action'].sudo().search([
            ('post_id', '=', post_rec.id),
            ('member_id', '=', member.id)
        ], limit=1)

        if old:
            old.write({'action_type': action_type})
            message = 'Post action updated'
        else:
            request.env['sica.mobile.post.action'].sudo().create({
                'post_id': post_rec.id,
                'member_id': member.id,
                'action_type': action_type,
            })
            message = 'Post action added'

        count = request.env['sica.mobile.post.action'].sudo().search_count([
            ('post_id', '=', post_rec.id)
        ])

        post_rec.write({'reaction_count': count})

        return self._json_response({
            'success': True,
            'message': message,
            'post_id': post_rec.id,
            'reaction_count': count
        })

    @http.route('/api/post/action/<int:post_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_post_actions(self, post_id, **kw):
        actions = request.env['sica.mobile.post.action'].sudo().search([
            ('post_id', '=', post_id)
        ])

        return self._json_response({
            'success': True,
            'post_id': post_id,
            'count': len(actions),
            'actions': [{
                'id': a.id,
                'membership_no': a.member_id.membership_no or '',
                'member_name': a.member_id.name or '',
                'action_type': a.action_type,
                'created_date': str(a.create_date),
            } for a in actions]
        })

    # ---------------------------------------------------------
    # COMMENTS API
    # ---------------------------------------------------------

    @http.route('/api/comments/<int:post_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_post_comments(self, post_id, **kw):
        comments = request.env['sica.mobile.comment'].sudo().search([
            ('post_id', '=', post_id)
        ], order='create_date asc')

        return self._json_response({
            'success': True,
            'post_id': post_id,
            'count': len(comments),
            'comments': [{
                'id': c.id,
                'membership_no': c.member_id.membership_no or '',
                'member_name': c.member_id.name or '',
                'member_image': self._member_image(c.member_id),
                'comment': c.comment or '',
                'created_date': str(c.create_date),
            } for c in comments]
        })

    @http.route('/api/comments', type='http', auth='public', methods=['POST'], csrf=False)
    def create_post_comment(self, **post):
        member = self._get_member_by_no(post.get('membership_no'))
        post_rec = request.env['sica.mobile.post'].sudo().browse(int(post.get('post_id') or 0))
        comment_text = post.get('comment') or ''

        if not member:
            return self._json_response({'success': False, 'error': 'Member not found'}, 404)

        if not post_rec.exists():
            return self._json_response({'success': False, 'error': 'Post not found'}, 404)

        if not comment_text:
            return self._json_response({'success': False, 'error': 'Comment is required'}, 400)

        comment = request.env['sica.mobile.comment'].sudo().create({
            'post_id': post_rec.id,
            'member_id': member.id,
            'comment': comment_text,
        })

        count = request.env['sica.mobile.comment'].sudo().search_count([
            ('post_id', '=', post_rec.id)
        ])

        post_rec.write({'comments_count': count})

        return self._json_response({
            'success': True,
            'message': 'Comment added successfully',
            'comment_id': comment.id,
            'comments_count': count
        }, 201)

    @http.route('/api/common/comments/<int:comment_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
    def delete_post_comment(self, comment_id, **kw):
        comment = request.env['sica.mobile.comment'].sudo().browse(comment_id)

        if not comment.exists():
            return self._json_response({'success': False, 'error': 'Comment not found'}, 404)

        post_rec = comment.post_id
        comment.unlink()

        count = request.env['sica.mobile.comment'].sudo().search_count([
            ('post_id', '=', post_rec.id)
        ])

        post_rec.write({'comments_count': count})

        return self._json_response({
            'success': True,
            'message': 'Comment deleted successfully',
            'comments_count': count
        })

    # ---------------------------------------------------------
    # EXPLORE API
    # ---------------------------------------------------------

    @http.route('/api/explore', type='http', auth='public', methods=['GET'], csrf=False)
    def explore_api(self, **kw):
        limit = int(kw.get('limit') or 10)
        member_number = kw.get('member_number') or kw.get('MEMBERSHIP_ID') or ''
        base_url = self._base_url()

        event_image_default_url = request.env['ir.config_parameter'].sudo().get_param(
            'website.event_image_link'
        ) or ''

        events = request.env['shooting.event'].sudo().search([], limit=limit, order="sequence asc")
        talents = request.env['member.job.seeker'].sudo().search([], limit=limit, order="create_date desc")
        opportunities = request.env['member.job.provider'].sudo().search([('state', '=', 'active')], order="create_date desc")        
        seen_members = set()     
        event_data = []
        talent_data = []
        opportunity_data = []

    # ---------------- EVENTS ----------------
        for event in events:
            attachments = []
            event_status = []
            complete_event_ids = []
            event_links = []

            for link in getattr(event, 'event_links_ids', []):
                event_links.append({'link': link.link or ''})

            for attachment in getattr(event, 'attachments_ids', []):
                attachment.public = True
                attachments.append(base_url + '/web/image/%s' % attachment.id)

            image = base_url + '/web/image?model=shooting.event&id=%s&field=image' % event.id

            if not attachments and event_image_default_url:
                attachments.append(event_image_default_url)

            for member_event in getattr(event, 'booking_status_ids', []):
                event_status.append({
                    'member_id': member_event.member_id.id if member_event.member_id else False,
                    'event_id': member_event.event_id.id if member_event.event_id else False,
                    'event_title': member_event.event_id.title if member_event.event_id else '',
                    'event_amount': member_event.event_id.amount if member_event.event_id else 0.0,
                    'payment_status': member_event.payment_status or '',
                    'booking_status': member_event.booking_status or '',
                    'event_book_id': member_event.id,
                })

            for complete_event in getattr(event, 'complete_event_ids', []):
                complete_event_attachments = []

                if getattr(complete_event, 'image', False):
                    complete_event_attachments.append(
                        base_url + '/get/complete_event/image/%s' % complete_event.id
                    )

                for attachment in getattr(complete_event, 'attachments_ids', []):
                    attachment.public = True
                    complete_event_attachments.append(base_url + '/web/image/%s' % attachment.id)

                if not complete_event_attachments and event_image_default_url:
                    complete_event_attachments.append(event_image_default_url)

                complete_event_ids.append({
                    'event_id': complete_event.event_id.id if complete_event.event_id else False,
                    'complete_event_images_url': complete_event_attachments,
                })

            is_member_booked = False
            if member_number:
                is_member_booked = True if event.booking_status_ids.filtered(
                    lambda x: x.member_id.membership_no == member_number and x.booking_status == 'Booked'
                ) else False


            event_data.append({
                'type': 'event',
                'event_id': event.id,
                'title': event.title or '',
                'description': event.description or '',
                'start_date': event.start_date.strftime("%Y-%m-%d") if event.start_date else '',
                'end_date': event.end_date.strftime("%Y-%m-%d") if event.end_date else '',
                'coach_name': event.coach_name or '',
                'amount': event.amount or 0.0,
                'image_url': image or '',
                'event_link': event.event_link or '',
                'is_completed': event.is_completed,
                'venue': event.venue or '',
                'time': event.time or '',
                'map': event.map or '',
                'program_presenters': event.program_presenters or '',
                'presised_by': event.presised_by or '',
                'chief_guest': event.chief_guest or '',
                'note': getattr(event, 'note', '') or getattr(event, 'notes', '') or '',
                'images_url': attachments,
                'booking_status': event_status or '',
                'complete_event_details': complete_event_ids or '',
                'is_member_booked': is_member_booked,
                'event_links': event_links,
                'created_date': str(event.create_date),
            })

    # ---------------- TALENTS / JOB SEEKER ----------------
        for job_seeker in talents:
            member = job_seeker.member_id

            talent_data.append({
                'type': 'talent',
                'id': job_seeker.id,
                'job_seeker_id': job_seeker.id,
                'name': job_seeker.name or '',

                'member_id': member.id if member else False,
                'member_name': job_seeker.member_name or '',
                'membership_no': job_seeker.membership_no or '',
                'member_image_url': '%s/get/public/image/res.member/%s/image_1920' % (base_url, member.id) if member and member.image_1920 else '',

                'mobile_number': job_seeker.mobile_number or (member.contact1 if member else ''),
                'contact1': member.contact1 if member else '',
                'contact2': member.contact2 if member else '',

                'designation': getattr(job_seeker, 'designation', '') or '',
                'grade': job_seeker.grade or '',

                'post_applying': job_seeker.post_applying_id.name if job_seeker.post_applying_id else '',
                'post_applying_id': job_seeker.post_applying_id.id if job_seeker.post_applying_id else False,

                'medium': job_seeker.medium_id.name if job_seeker.medium_id else '',
                'medium_id': job_seeker.medium_id.id if job_seeker.medium_id else False,
                'format_name': job_seeker.medium_id.name if job_seeker.medium_id else '',
                'format_id': job_seeker.medium_id.id if job_seeker.medium_id else False,

                'skills': [{'id': skill.id, 'name': skill.name} for skill in job_seeker.skill_ids],
                'skill_ids': [{'id': skill.id, 'name': skill.name} for skill in job_seeker.skill_ids],

                'start_date': job_seeker.start_date.strftime("%Y-%m-%d") if job_seeker.start_date else '',
                'till_date': job_seeker.till_date.strftime("%Y-%m-%d") if job_seeker.till_date else '',

                'experience': getattr(job_seeker, 'experience', False),
                'portfolio_link': job_seeker.portifolio_link or '',
                'portifolio_link': job_seeker.portifolio_link or '',
                'portfolio_link_2': job_seeker.portifolio_link_2 or '',
                'portifolio_link_2': job_seeker.portifolio_link_2 or '',
                'note': job_seeker.note or '',

                'has_document': True if job_seeker.document else False,
                'document_url': '%s/web/content?model=member.job.seeker&id=%s&field=document&download=true' % (base_url, job_seeker.id) if job_seeker.document else '',

                'state': getattr(job_seeker, 'state', '') or '',
                'active': getattr(job_seeker, 'active', True),
                'created_date': str(job_seeker.create_date),
            })

    # ---------------- OPPORTUNITIES / JOB PROVIDER ----------------
        for job_provider in opportunities:

            provider_skills = []

            if job_provider.skill_ids:
                provider_skills = [
                    {'id': s.id, 'name': s.name}
                    for s in job_provider.skill_ids
                ]

            elif job_provider.skill:
                provider_skills = [
                    {'id': False, 'name': job_provider.skill}
                ]
            if member and member.id in seen_members:
                continue

            if member:
                seen_members.add(member.id)
  
            member = job_provider.member_id

            opportunity_data.append({
                'type': 'opportunity',
                'id': job_provider.id,
                'job_provider_id': job_provider.id,
                'name': job_provider.name or '',

                'member_id': member.id if member else False,
                'member_name': job_provider.member_name or '',
                'membership_no': job_provider.membership_no or '',
                'member_image_url': '%s/get/public/image/res.member/%s/image_1920' % (base_url, member.id) if member and member.image_1920 else '',
                'mobile_number': job_provider.mobile_number or '',
                'contact1': member.contact1 if member else '',
                'contact2': member.contact2 if member else '',
                'designation': job_provider.grade or '',
                'grade': job_provider.grade or '',
                'post_required': job_provider.post_required_id.name if job_provider.post_required_id else '',
                'post_required_id': job_provider.post_required_id.id if job_provider.post_required_id else False,
                'skills': provider_skills,
                'medium': job_provider.medium_id.name if job_provider.medium_id else '',
                'medium_id': job_provider.medium_id.id if job_provider.medium_id else False,
                'available_start_date': job_provider.required_from.strftime("%Y-%m-%d") if job_provider.required_from else '',
                'available_end_date': job_provider.required_till.strftime("%Y-%m-%d") if job_provider.required_till else '',
                'required_from': job_provider.required_from.strftime("%Y-%m-%d") if job_provider.required_from else '',
                'required_till': job_provider.required_till.strftime("%Y-%m-%d") if job_provider.required_till else '',
                'note': job_provider.note or getattr(job_provider, 'description', '') or '',
                'created_date': str(job_provider.create_date),
            })

        return self._json_response({
            'success': True,
            'events': event_data,
            'talents': talent_data,
            'opportunities': opportunity_data,
        })
    # ---------------------------------------------------------
    # FOLLOW / UNFOLLOW API
    # ---------------------------------------------------------

    @http.route('/api/follow', type='http', auth='public', methods=['POST'], csrf=False)
    def follow_user(self, **post):
        follower = self._get_member_by_no(post.get('membership_no'))
        following = self._get_member_by_no(post.get('following_membership_no'))

        if not follower or not following:
            return self._json_response({'success': False, 'error': 'Member not found'}, 404)

        if follower.id == following.id:
            return self._json_response({'success': False, 'error': 'Cannot follow yourself'}, 400)

        old = request.env['sica.mobile.follow'].sudo().search([
            ('follower_id', '=', follower.id),
            ('following_id', '=', following.id)
        ], limit=1)

        if not old:
            request.env['sica.mobile.follow'].sudo().create({
                'follower_id': follower.id,
                'following_id': following.id
            })

        return self._json_response({
            'success': True,
            'message': 'Followed successfully'
        })

    @http.route('/api/unfollow', type='http', auth='public', methods=['POST'], csrf=False)
    def unfollow_user(self, **post):
        follower = self._get_member_by_no(post.get('membership_no'))
        following = self._get_member_by_no(post.get('following_membership_no'))

        if not follower or not following:
            return self._json_response({'success': False, 'error': 'Member not found'}, 404)

        rec = request.env['sica.mobile.follow'].sudo().search([
            ('follower_id', '=', follower.id),
            ('following_id', '=', following.id)
        ], limit=1)

        if rec:
            rec.unlink()

        return self._json_response({
            'success': True,
            'message': 'Unfollowed successfully'
        })
    
    # ---------------------------------------------------------
    # COMMON COMMENTS API
    # news, blog, tech_talk, gallery
    # ---------------------------------------------------------

    @http.route('/api/common/comments', type='http', auth='public', methods=['POST'], csrf=False)
    def create_common_comment(self, **post):
        membership_no = post.get('membership_no')
        source_type = post.get('source_type')
        source_id = int(post.get('source_id') or 0)
        comment_text = post.get('comment') or ''

        member = self._get_member_by_no(membership_no)

        if not member:
            return self._json_response({'success': False, 'error': 'Member not found'}, 404)

        if source_type not in ['news', 'blog', 'tech_talk', 'gallery']:
            return self._json_response({'success': False, 'error': 'Invalid source_type'}, 400)

        if not source_id:
            return self._json_response({'success': False, 'error': 'source_id is required'}, 400)

        if not comment_text:
            return self._json_response({'success': False, 'error': 'comment is required'}, 400)

        rec = request.env['sica.common.comment'].sudo().create({
            'source_type': source_type,
            'source_id': source_id,
            'member_id': member.id,
            'comment': comment_text,
        })

        return self._json_response({
            'success': True,
            'message': 'Comment added successfully',
            'comment_id': rec.id,
            'source_type': source_type,
            'source_id': source_id,
        }, 201)


    @http.route('/api/common/comments/<string:source_type>/<int:source_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_common_comments(self, source_type, source_id, **kw):

        comments = request.env['sica.common.comment'].sudo().search([
            ('source_type', '=', source_type),
            ('source_id', '=', source_id)
        ], order='create_date asc')

        return self._json_response({
            'success': True,
            'source_type': source_type,
            'source_id': source_id,
            'count': len(comments),
            'comments': [{
                'id': c.id,
                'membership_no': c.member_id.membership_no or '',
                'member_name': c.member_id.name or '',
                'member_image': self._member_image(c.member_id),
                'comment': c.comment or '',
                'created_date': str(c.create_date),
            } for c in comments]
        })


    @http.route('/api/comments/<int:comment_id>',
            type='http', auth='public', methods=['DELETE'], csrf=False)
    def delete_common_comment(self, comment_id, **kw):

        comment = request.env['sica.common.comment'].sudo().browse(comment_id)

        if not comment.exists():
            return self._json_response({'success': False, 'error': 'Comment not found'}, 404)

        comment.unlink()

        return self._json_response({
            'success': True,
            'message': 'Comment deleted successfully'
        })