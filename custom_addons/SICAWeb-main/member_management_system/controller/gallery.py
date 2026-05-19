from odoo import http, fields
from odoo.http import request
import json

class Gallery(http.Controller):
    @http.route('/get/all/gallery/category', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_all_gallery_category(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url.image')
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        gallery_category_ids = request.env['sica.gallery.category'].sudo().search([])
        category_details = []
        for category in gallery_category_ids:
            gallery_ids = request.env['sica.gallery'].sudo().search([('category_id', '=', category.id)])

            category_details.append({
                'category_name': category.name,
                'category_id': category.id,
                'galleries': [
                    {
                        'id': gallery.id,
                        'name': gallery.name or '',
                        'description': gallery.description or '',
                        'date': gallery.date.strftime("%Y-%m-%d") if gallery.date else '',
                        'images': [
                            {
                                'id': image.id,
                                'title': image.title or '',
                                'description': image.description or '',
                                'image': base_url + '/web/image?' + 'model=gallery.image&id=' + str(image.id) + '&field=image' or '',
                            }
                            for image in gallery.gallery_image_ids
                        ]
                    }
                    for gallery in gallery_ids
                ]
            })
        return json.dumps({'gallery_category_details': category_details})

    @http.route('/get/gallery', type='http', auth='none', methods=['GET', 'POST'], csrf=False)
    def action_get_gallery(self, **kw):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url.image')
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        category_id = kw.get('category_id')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')
        event_image_default_url = request.env['ir.config_parameter'].sudo().get_param('website.event_image_link')

        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        gallery_category_ids = request.env['sica.gallery'].sudo().search([('category_id', '=', int(category_id))])
        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        gallery_details = []
        for gallery in gallery_category_ids:

            gallery_comments = []
            gallery_likes = []

            is_member_like = ''
            member_like = gallery.gallery_like_ids.filtered(lambda x: x.member_id.id == member.id)
            if member_like:
                is_member_like = True
            else:
                is_member_like = False
            for comment in gallery.gallery_comment_ids:
                gallery_comments.append({
                    'member_name': comment.member_id.name or '',
                    'comment': comment.remark or '',
                    'create_date': comment.create_date.strftime(
                        "%Y-%m-%d %H:%M:%S") if comment.create_date else '',
                    'member_number': comment.member_id.membership_no or '',
                    'comment_id': comment.id or '',
                    'member_image_url': base_url + '/web/image?' + 'model=res.member&id=' + str(comment.member_id.id) + '&field=image_1920' or '',
                    'member_image': str(comment.member_id.image_512) if comment.member_id and comment.member_id.image_512 else '',
                    'is_member_like': is_member_like,
                })

            for gallery_like in gallery.gallery_like_ids:
                gallery_likes.append({
                    'member_name': gallery_like.member_id.name if gallery_like.member_id else '',
                    'like_id': gallery_like.id,
                    'member_image_url': base_url + '/web/image?' + 'model=res.member&id=' + str(gallery_like.member_id.id) + '&field=image_1920' or '',
                })

            attachments = []
            for attachment in gallery.attachments_ids:
                attachment.public = True
                attachments.append(base_url + '/web/image/%s' % attachment.id)
            if not attachments:
                attachments.append(event_image_default_url)

            gallery_details.append({
                'name': gallery.name,
                'description': gallery.description,
                'image_url': base_url + '/web/image?' + 'model=sica.gallery&id=' + str(
                    gallery.id) + '&field=photo' or '',
                'image': str(gallery.photo) if gallery.photo else '',
                'date': gallery.date.strftime("%Y-%m-%d") if gallery.date else '',
                'like_count': len(gallery.gallery_like_ids),
                'comment': len(gallery.gallery_comment_ids),
                'gallery_id': gallery.id,
                'comments': gallery_comments,
                'likes': gallery_likes,
                'attachments': attachments
            })

        return json.dumps({'gallery_details': gallery_details})

    @http.route('/post/gallery/like', type='http', auth='none', methods=['POST', 'GET'], csrf=False)
    def action_post_gallery_like(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        gallery_id = kw.get('gallery_id')
        data = kw.get('data')
        data = data.replace("'", '"')
        data_dict = json.loads(data)
        member_id = data_dict.get('member_id') or ''
        member_name = data_dict.get('member_name') or ''
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        gallery_id = request.env['sica.gallery'].sudo().search([('id', '=', int(gallery_id))])
        member = request.env['res.member'].sudo().search([('membership_no', '=', member_id)], limit=1)
        if member:
            member_gallery_like_id = gallery_id.gallery_like_ids.filtered(lambda x: x.member_id.id == member.id)

            if member_gallery_like_id:
                member_gallery_like_id.sudo().unlink()
            else:
                gallery_like = request.env['gallery.like'].sudo().create({
                    'member_id': member.id,
                    'member_name': member_name,
                    'remark': 'Like',
                    'gallery_id': gallery_id.id,
                })

        return json.dumps({'gallery_like_update': 'Successful'})

    @http.route('/post/gallery/create/comment', type='http', auth='none', methods=['POST'], csrf=False)
    def action_gallery_post_comment(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        gallery_id = kw.get('gallery_id')
        data = kw.get('data')
        data = data.replace("'", '"')
        data_dict = json.loads(data)
        member_id = data_dict.get('member_id') or ''
        member_name = data_dict.get('member_name') or ''
        comment = data_dict.get('comment') or ''
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        gallery_id = request.env['sica.gallery'].sudo().search([('id', '=', int(gallery_id))])
        member = request.env['res.member'].sudo().search([('membership_no', '=', member_id)], limit=1)
        gallery_like = request.env['gallery.comment'].sudo().create({
            'member_id': member.id,
            'member_name': member_name,
            'remark': comment,
            'duplicate_gallery_id': gallery_id.id,
            'approve_status': 'Waiting_for_Approval',
            'request_type': 'Create',
            'gallery_image': gallery_id.photo,
            'gallery_id': gallery_id.id
        })

        return json.dumps({'gallery_comment_create': 'Successful'})

    @http.route('/post/gallery/update/comment', type='http', auth='none', methods=['POST'], csrf=False)
    def action_gallery_update_comment(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        gallery_id = kw.get('gallery_id')
        data = kw.get('data')
        data = data.replace("'", '"')
        data_dict = json.loads(data)
        member_id = data_dict.get('member_id') or ''
        member_name = data_dict.get('member_name') or ''
        comment = data_dict.get('comment') or ''
        comment_id = data_dict.get('comment_id') or ''
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        gallery_id = request.env['sica.gallery'].sudo().search([('id', '=', int(gallery_id))])
        member = request.env['res.member'].sudo().search([('membership_no', '=', member_id)], limit=1)
        gallery_comment_id = request.env['gallery.comment'].sudo().search([('id', '=', int(comment_id))], limit=1)
        gallery_comment = gallery_comment_id.sudo().write({
            'member_id': member.id,
            'member_name': member_name,
            'remark': comment,
            'duplicate_gallery_id': gallery_id.id,
            'gallery_id': gallery_id.id,
            'approve_status': 'Waiting_for_Approval',
            'request_type': 'Update',
            'gallery_image': gallery_id.photo
        })

        return json.dumps({'gallery_comment_update': 'Successful'})

    @http.route('/post/gallery/delete/comment', type='http', auth='none', methods=['POST'], csrf=False)
    def action_gallery_delete_comment(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        gallery_id = kw.get('gallery_id')
        data = kw.get('data')
        data = data.replace("'", '"')
        data_dict = json.loads(data)
        member_id = data_dict.get('member_id') or ''
        member_name = data_dict.get('member_name') or ''
        comment = data_dict.get('comment') or ''
        comment_id = data_dict.get('comment_id') or ''
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        gallery_id = request.env['sica.gallery'].sudo().search([('id', '=', int(gallery_id))])
        member = request.env['res.member'].sudo().search([('membership_no', '=', member_id)], limit=1)
        gallery_comment_id = request.env['gallery.comment'].sudo().search([('id', '=', int(comment_id))], limit=1)
        if gallery_comment_id:
            gallery_comment_id.sudo().unlink()
        # gallery_like = gallery_comment_id.sudo().write({
        #     'member_id': member.id,
        #     'member_name': member_name,
        #     'remark': comment,
        #     'gallery_id': gallery_id.id,
        #     'approve_status': 'Waiting_for_Approval',
        #     'request_type': 'Delete',
        #     'gallery_image': gallery_id.photo
        # })

        return json.dumps({'gallery_comment_delete': 'Successful'})
