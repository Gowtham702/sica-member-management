import re
import json
import base64
from odoo import http
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
        return request.env['res.member'].sudo().search([
            ('membership_no', '=', str(membership_no))
        ], limit=1)

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
            'image_url': '%s/api/shootings/image/%s' % (base_url, shoot.id) if shoot.image else '',
            'movie_poster_url': '%s/api/shootings/poster/%s' % (base_url, shoot.id) if shoot.movie_poster else '',
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
        team_ids = []
        if post.get('team_membership_nos'):
            membership_nos = [x.strip() for x in post.get('team_membership_nos').split(',') if x.strip()]
            team_ids = request.env['res.member'].sudo().search([('membership_no', 'in', membership_nos)]).ids

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

    @http.route('/api/shootings/<int:shoot_id>', type='http', auth='public', methods=['PUT', 'POST'], csrf=False)
    def update_shooting(self, shoot_id, **post):
        rec = request.env['sica.mobile.shooting'].sudo().browse(shoot_id)
        if not rec.exists():
            return self._json_response({'success': False, 'error': 'Shooting not found'}, 404)

        vals = {}

        for field in ['title', 'description', 'location', 'production_house', 'from_date', 'to_date', 'status']:
            if post.get(field):
                vals[field] = post.get(field)

        if post.get('team_membership_nos'):
            membership_nos = [x.strip() for x in post.get('team_membership_nos').split(',') if x.strip()]
            members = request.env['res.member'].sudo().search([('membership_no', 'in', membership_nos)])
            vals['team_member_ids'] = [(6, 0, members.ids)]

        image_file = post.get('image')
        if image_file:
            vals['image'] = base64.b64encode(image_file.read()).decode('utf-8')
            vals['image_filename'] = image_file.filename

        poster_file = post.get('movie_poster')
        if poster_file:
            vals['movie_poster'] = base64.b64encode(poster_file.read()).decode('utf-8')
            vals['movie_poster_filename'] = poster_file.filename

        rec.write(vals)
        return self._json_response({'success': True, 'message': 'Shooting updated successfully', 'shooting': self._shooting_vals(rec)})

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

    @http.route('/api/comments/<int:comment_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
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
        base_url = self._base_url()

        opportunities = request.env['member.job.provider'].sudo().search([], limit=limit, order='create_date desc')
        talents = request.env['member.job.seeker'].sudo().search([], limit=limit, order='create_date desc')
        events = request.env['shooting.event'].sudo().search([], limit=limit, order='create_date desc')

        data = []

        for opp in opportunities:
            member = getattr(opp, 'member_id', False)
            data.append({
                'type': 'opportunity',
                'id': opp.id,
                'member_name': member.name if member else getattr(opp, 'name', '') or '',
                'membership_number': member.membership_no if member else '',
                'member_image_url': self._member_image(member) if member else '',
                'title': getattr(opp, 'title', '') or getattr(opp, 'name', '') or '',
                'description': getattr(opp, 'description', '') or '',
                'location': getattr(opp, 'location', '') or '',
                'created_date': str(opp.create_date),
            })

        for talent in talents:
            member = getattr(talent, 'member_id', False)
            data.append({
                'type': 'talent',
                'id': talent.id,
                'member_name': member.name if member else getattr(talent, 'name', '') or '',
                'membership_number': member.membership_no if member else getattr(talent, 'membership_no', '') or '',
                'member_image_url': self._member_image(member) if member else '',
                'post_applying': getattr(talent, 'post_applying', '') or getattr(talent, 'name', '') or '',
                'experience': getattr(talent, 'experience', '') or '',
                'mobile': getattr(talent, 'mobile', '') or '',
                'email': getattr(talent, 'email', '') or '',
                'created_date': str(talent.create_date),
            })

        for event in events:
            data.append({
                'type': 'event',
                'event_id': event.id,
                'title': getattr(event, 'title', '') or getattr(event, 'name', '') or '',
                'image_url': '%s/web/image?model=shooting.event&id=%s&field=image' % (base_url, event.id),
                'date': str(getattr(event, 'date', '')) if getattr(event, 'date', False) else '',
                'description': getattr(event, 'description', '') or '',
                'location': getattr(event, 'location', '') or '',
                'created_date': str(event.create_date),
            })

        return self._json_response({
            'success': True,
            'data': data
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