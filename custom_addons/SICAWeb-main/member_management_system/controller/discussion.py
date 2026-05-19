import binascii

from odoo import http, fields
from odoo.http import request
import json
import base64
import io
from PIL import Image


class MemberDiscussion(http.Controller):
    @http.route('/get/all/topic', type='http', auth='none', methods=['GET'], csrf=False)
    def get_all_topic(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        if not api_key or api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        discussions_topic_ids = request.env['discussion.forum'].sudo().search([])
        discussion_topic = []
        for topic in discussions_topic_ids:
            discussion_vals = {
                'topic': topic.discussion_topic or '',
                'discussion_id': topic.id
            }
            discussion_topic.append(discussion_vals)
        return json.dumps({'discussion_topic': discussion_topic})

    @http.route('/get/topic/comments', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_topic_comments(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        if not api_key or api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        topic_id = int(kw.get('topic_id'))
        discussion = request.env['discussion.forum'].sudo().browse(topic_id)
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url.image')
        discussion_comment_vals = []
        comment_ids = sorted(discussion.discussion_comment_ids, key=lambda x: x.id, reverse=True)
        for comment in comment_ids:
            profile_image = base_url + '/web/image?model=res.member&id=' + str(
                comment.member_id.id) + '&field=image_1920'
            discussion_comment = {
                'profile_image': profile_image,
                'comment': comment.comment or '',
                'comment_create_date': comment.create_date.strftime(
                    "%Y-%m-%d %H:%M:%S") if comment.create_date else '',
                'member_name': comment.member_id.name or '',
                'membership_no': comment.member_id.membership_no or '',
                'designation': comment.member_id.designation or '',
                'comment_id': comment.id,
            }
            if comment.image:
                discussion_comment['image_url'] = base_url + '/web/image?model=discussion.comment&id=' + str(
                    comment.id) + '&field=image'
            discussion_comment_vals.append(discussion_comment)

        return json.dumps({'discussion_comment_details': discussion_comment_vals})

    @http.route('/get/topic/child_comments', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_child_comments(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        if not api_key or api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        comment_id = int(kw.get('comment_id'))
        comment = request.env['discussion.comment'].sudo().browse(comment_id)
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url.image')
        child_comments = []
        child_comment_ids = sorted(comment.child_comment_ids, key=lambda x: x.id, reverse=False)
        for child_comment in child_comment_ids:
            child_profile_image = base_url + '/web/image?model=res.member&id=' + str(
                child_comment.member_id.id) + '&field=image_1920'
            child_discussion_comment = {
                'profile_image': child_profile_image,
                'comment': child_comment.comment or '',
                'comment_create_date': child_comment.create_date.strftime(
                    "%Y-%m-%d %H:%M:%S") if child_comment.create_date else '',
                'member_name': child_comment.member_id.name or '',
                'membership_no': child_comment.member_id.membership_no or '',
                'designation': child_comment.member_id.designation or '',
                'comment_id': comment.id,
                'child_comment_id': child_comment.id
            }
            if child_comment.image:
                child_discussion_comment[
                    'image_url'] = base_url + '/web/image?model=discussion.comment&id=' + str(
                    child_comment.id) + '&field=image'
            child_comments.append(child_discussion_comment)
        return json.dumps({'discussion_child_comment_details': child_comments})


    @http.route('/get/topic/discussion', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_topic_based_discussion(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        if not api_key or api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        topic_id = int(kw.get('topic_id'))

        discussion_topic = request.env['discussion.forum'].sudo().browse(topic_id)
        discussion_details = []
        for discussion in discussion_topic:
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url.image')
            image = base_url + '/web/image?model=res.member&id=' + str(discussion.member_id.id) + '&field=image_1920'

            last_comment = discussion.discussion_comment_ids.sorted('id', reverse=True)[:1]
            last_comment_member_image = base_url + '/web/image?model=res.member&id=' + str(
                last_comment.member_id.id) + '&field=image_1920'

            discussion_vals = {
                'profile': image,
                'topic': discussion.discussion_topic or '',
                'member_name': discussion.member_id.name or '',
                'category_name': discussion.category_id.name,
                'category_id': discussion.category_id.id,
                'discussion_id': discussion.id,
                'create_date': discussion.create_date.strftime("%Y-%m-%d %H:%M:%S") if discussion.create_date else '',
                'member_id': discussion.member_id.id,
                'designation': discussion.member_id.designation,
                'last_member_name': last_comment.member_id.name or '',
                'last_topic_create_date': last_comment.create_date.strftime(
                    "%Y-%m-%d %H:%M:%S") if last_comment.create_date else '',
                'last_commit_member_image': last_comment_member_image
            }
            discussion_details.append(
                {'discussion_details': discussion_vals})

        return json.dumps({'discussion_forum_details': discussion_details})


    @http.route('/get/all/member_details/discussion', type='http', auth='none', methods=['GET'], csrf=False)
    def get_member_details_discussion_forum(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url.image')

        if not api_key or api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})

        user_membership_id = kw.get('user_member_no')
        member_membership_id = kw.get('member_no')

        if not user_membership_id:
            return json.dumps({"error": "Membership ID is missing"})

        user_member = request.env['res.member'].sudo().search([('membership_no', '=', user_membership_id)], limit=1)
        member = request.env['res.member'].sudo().search([('membership_no', '=', member_membership_id)], limit=1)

        if not member or not user_member:
            return json.dumps({"error": "Invalid Membership IDs"})

        topics = []
        user_topic_ids = request.env['discussion.forum'].sudo().search(
            ['|', ('member_id', '=', member.id), ('member_id', '=', user_member.id)])
        topics.extend(user_topic_ids.ids)

        user_comment_topic_ids = request.env['discussion.comment'].sudo().search(
            ['|', ('member_id', '=', member.id), ('member_id', '=', user_member.id)])
        for topic in user_comment_topic_ids:
            if topic.discussion_id.id not in topics:
                topics.append(topic.discussion_id.id)

        discussion_form = []
        for discussion_id in topics:
            user_discussion = request.env['discussion.forum'].sudo().browse(discussion_id)
            if not user_discussion:
                continue

            image = ''
            if user_discussion.member_id.image_1920:
                image = base_url + '/web/image?' + 'model=res.member&id=' + str(
                    user_discussion.member_id.id) + '&field=image_1920'

            discussion_vals = {
                'profile': image,
                'topic': user_discussion.discussion_topic,
                'member_name': user_discussion.member_id.name,
                'category_name': user_discussion.category_id.name,
                'category_id': user_discussion.category_id.id,
                'discussion_id': user_discussion.id,
                'create_date': user_discussion.create_date.strftime(
                    "%Y-%m-%d %H:%M:%S") if user_discussion.create_date else '',
                'member_id': user_discussion.member_id.id,
                'designation': user_discussion.member_id.designation,
            }

            discussion_comment_vals = []
            comment_ids = sorted(user_discussion.discussion_comment_ids, key=lambda x: x.id, reverse=True)
            for comment in comment_ids:
                if comment.member_id.id == member.id or comment.member_id.id == user_member.id:
                    profile_image = base_url + '/web/image?' + 'model=res.member&id=' + str(
                        comment.member_id.id) + '&field=image_1920'
                    comment_vals = {
                        'profile_image': profile_image,
                        'comment': comment.comment or '',
                        'comment_create_date': comment.create_date.strftime(
                            "%Y-%m-%d %H:%M:%S") if comment.create_date else '',
                        'member_name': comment.member_id.name or '',
                        'designation': comment.member_id.designation or '',
                        'comment_id': comment.id,
                    }
                    if comment.image:
                        comment_vals['image_url'] = base_url + '/web/image?' + 'model=discussion.comment&id=' + str(
                            comment.id) + '&field=image'

                    child_discussion_comments = []
                    for child_comment in comment.child_comment_ids:
                        profile_image = base_url + '/web/image?' + 'model=res.member&id=' + str(
                            child_comment.member_id.id) + '&field=image_1920'
                        child_comment_vals = {
                            'profile_image': profile_image,
                            'comment': child_comment.comment or '',
                            'comment_create_date': child_comment.create_date.strftime(
                                "%Y-%m-%d %H:%M:%S") if child_comment.create_date else '',
                            'member_name': child_comment.member_id.name or '',
                            'designation': child_comment.member_id.designation or '',
                            'comment_id': child_comment.id,
                            'child_comment_id': child_comment.id,
                        }
                        if child_comment.image:
                            child_comment_vals[
                                'image_url'] = base_url + '/web/image?' + 'model=child.discussion.comment&id=' + str(
                                child_comment.id) + '&field=image'
                        child_discussion_comments.append(child_comment_vals)
                    comment_vals['child_comment_vals'] = child_discussion_comments
                    discussion_comment_vals.append(comment_vals)

            discussion_form.append({'topic': discussion_vals, 'discussion_comments': discussion_comment_vals})

        return json.dumps({'discussion_forum': discussion_form})

    @http.route('/get/all/discuss_category', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_discuss_category(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url.image')
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        discuss_category_ids = request.env['discuss.category'].sudo().search([])
        category_details = []
        for category in discuss_category_ids:
            discuss_topic = request.env['discussion.forum']
            topic_count = discuss_topic.sudo().search_count([('category_id', '=', category.id)])
            topic_ids = discuss_topic.sudo().search([('category_id', '=', category.id)])
            replies = 0
            for comment in topic_ids:
                replies += len(comment.discussion_comment_ids)
            topic_id = discuss_topic.sudo().search([('category_id', '=', category.id)], order='id desc', limit=1)
            member_image = ''
            category_description = ''
            if category.description:
                category_description = category.description
            if topic_id.member_id.image_1920:
                member_image = base_url + '/web/image?' + 'model=res.member&id=' + str(
                    topic_id.member_id.id) + '&field=image_1920'
            category_details.append({
                'category_name': category.name,
                'category_description': category_description or '',
                'category_id': category.id,
                'topic_count': topic_count,
                'replies': replies,
                'last_member_name': topic_id.member_id.name or '',
                'last_topic_create_date': topic_id.create_date.strftime(
                    "%Y-%m-%d  %H:%M:%S") if topic_id.create_date else '',
                'member_image': member_image
            })
        return json.dumps({'discuss_category_details': category_details})

    @http.route('/get/all/discussion_topic', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_all_discussion_details(self, **kw):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url.image')
        api_key = kw.get('api_key')
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"

        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})

        offset = int(kw.get('offset', 0))
        limit = int(kw.get('limit', 10))
        category_id = int(kw.get('category_id'))

        category = request.env['discuss.category'].sudo().browse(category_id)
        if not category:
            return json.dumps({"error": "Invalid category ID"})

        discussions = request.env['discussion.forum'].sudo().search([('category_id', '=', category_id)], offset=offset,
                                                                    limit=limit)
        discussion_details = []

        for discussion in discussions:
            image = base_url + '/web/image?model=res.member&id=' + str(discussion.member_id.id) + '&field=image_1920'

            last_comment = discussion.discussion_comment_ids.sorted('id', reverse=False)[:1]
            last_comment_member_image = base_url + '/web/image?model=res.member&id=' + str(
                last_comment.member_id.id) + '&field=image_1920'

            discussion_vals = {
                'profile': image,
                'topic': discussion.discussion_topic or '',
                'member_name': discussion.member_id.name or '',
                'category_name': category.name,
                'category_id': category.id,
                'discussion_id': discussion.id,
                'create_date': discussion.create_date.strftime("%Y-%m-%d %H:%M:%S") if discussion.create_date else '',
                'member_id': discussion.member_id.id,
                'designation': discussion.member_id.designation,
                'last_member_name': last_comment.member_id.name or '',
                'last_topic_create_date': last_comment.create_date.strftime(
                    "%Y-%m-%d %H:%M:%S") if last_comment.create_date else '',
                'last_commit_member_image': last_comment_member_image
            }

            discussion_comment_vals = []
            comment_ids = sorted(discussion.discussion_comment_ids, key=lambda x: x.id, reverse=False)
            for comment in comment_ids:
                profile_image = base_url + '/web/image?model=res.member&id=' + str(
                    comment.member_id.id) + '&field=image_1920'
                discussion_comment = {
                    'profile_image': profile_image,
                    'comment': comment.comment or '',
                    'comment_create_date': comment.create_date.strftime(
                        "%Y-%m-%d %H:%M:%S") if comment.create_date else '',
                    'member_name': comment.member_id.name or '',
                    'membership_no': comment.member_id.membership_no or '',
                    'designation': comment.member_id.designation or '',
                    'comment_id': comment.id,
                }
                if comment.image:
                    discussion_comment['image_url'] = base_url + '/web/image?model=discussion.comment&id=' + str(
                        comment.id) + '&field=image'

                child_comments = []
                for child_comment in comment.child_comment_ids:
                    child_profile_image = base_url + '/web/image?model=res.member&id=' + str(
                        child_comment.member_id.id) + '&field=image_1920'
                    child_discussion_comment = {
                        'profile_image': child_profile_image,
                        'comment': child_comment.comment or '',
                        'comment_create_date': child_comment.create_date.strftime(
                            "%Y-%m-%d %H:%M:%S") if child_comment.create_date else '',
                        'member_name': child_comment.member_id.name or '',
                        'membership_no': child_comment.member_id.membership_no or '',
                        'designation': child_comment.member_id.designation or '',
                        'comment_id': comment.id,
                        'child_comment_id': child_comment.id
                    }
                    if child_comment.image:
                        child_discussion_comment[
                            'image_url'] = base_url + '/web/image?model=discussion.comment&id=' + str(
                            child_comment.id) + '&field=image'
                    child_comments.append(child_discussion_comment)

                discussion_comment['child_discussion_comments'] = child_comments
                discussion_comment_vals.append(discussion_comment)

            discussion_details.append(
                {'discussion_details': discussion_vals, 'discussion_comments': discussion_comment_vals})

        return json.dumps({'discussion_forum_details': discussion_details})

    @http.route('/create/discussion_topic', type='http', auth='none', methods=['POST'], csrf=False)
    def action_create_discussion_topic(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        data = kw.get('data')
        data = data.replace("'", '"')
        data_dict = json.loads(data)
        discussion_topic = data_dict.get('discussion_topic')
        category = data_dict.get('category_id')
        category_id = request.env['discuss.category'].sudo().search([('id', '=', category)], limit=1)

        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        if member:
            create_discussion = request.env['discussion.forum'].sudo().create({
                'discussion_topic': discussion_topic or '',
                'member_id': member.id or False,
                'category_id': category_id.id or False
            })
            response_data = {
                'Discussion': 'discussion_created',
                'Discussion ID': create_discussion.id,
                "Discussion Topic Details": {
                    'discussion_topic': create_discussion.discussion_topic or '',
                    'member_id': create_discussion.member_id.id or False,
                    'membership_no': create_discussion.member_id.membership_no or '',
                    'category_id': create_discussion.category_id.id or False,  # Fixing the typo here
                    'discussion_topic_id': create_discussion.id or False
                }
            }

            return json.dumps(response_data)
        else:
            return json.dumps({"error": "Membership ID is mismatched"})

    @http.route('/update/discussion_topic', type='http', auth='none', methods=['POST'], csrf=False)
    def action_update_discussion_topic(self, **kw):
        discussion_id = kw.get('DISCUSSION_ID')
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        data = kw.get('data')
        data = data.replace("'", '"')
        data_dict = json.loads(data)
        topic = data_dict.get('topic')

        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        if member:
            discussion_id = request.env['discussion.forum'].sudo().search(
                [('id', '=', discussion_id)], limit=1)
            if discussion_id:
                update_discuss = discussion_id.sudo().write({
                    'discussion_topic': topic,
                    'member_id': member.id,
                })
                return json.dumps({'discuss': 'discuss_updated', 'Discussion ID': discussion_id.id})
            else:
                return json.dumps({'error': 'Id is not Mismatched'})
        else:
            return json.dumps({"error": "Membership ID is mismatched"})

    @http.route('/delete/discussion_topic', type='http', auth='none', methods=['DELETE'], csrf=False)
    def action_delete_discussion_topic(self, **kw):
        api_key = kw.get('api_key')
        discussion_id = kw.get('DISCUSSION_ID')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})

        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        if member:
            discussion = request.env['discussion.forum'].sudo().search(
                [('member_id', '=', member.id), ('id', '=', discussion_id)], limit=1)
            if discussion:
                discussion.sudo().unlink()
                return json.dumps({'discussion': 'discussion_deleted'})
            else:
                return json.dumps({'error': "Record not found"})

        else:
            return json.dumps({"error": "Membership ID is mismatched"})

    @http.route('/create/discussion_comment', type='http', auth='none', methods=['POST'], csrf=False)
    def action_create_discussion_comment(self, **kw):
        discussion_id = kw.get('DISCUSSION_ID')
        if not discussion_id:
            return json.dumps({"error": "Discussion ID Not found"})

        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        data = kw.get('data')
        data = data.replace("'", '"')
        data_dict = json.loads(data)
        document = data_dict.get('document')
        comment = data_dict.get('comment')
        discussion_id = request.env['discussion.forum'].sudo().search([('id', '=', discussion_id)], limit=1)
        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        if member:
            create_discussion_comment = request.env['discussion.comment'].sudo().create({
                'member_id': member.id or False,
                'discussion_id': discussion_id.id or False,
                'document': document or '',
            })
            if document:
                document = document.replace(" ", "+")
                create_discussion_comment.write({'image': document})
            if comment:
                create_discussion_comment.write({'comment': comment})
            return json.dumps({'Discussion': 'comment_created', 'Comment ID': create_discussion_comment.id})
        else:
            return json.dumps({"error": "Membership ID is mismatched"})

    @http.route('/create/discussion_comment/json', type="json", auth='none', methods=['POST'], csrf=False)
    def action_create_discussion_comment_json(self, **kw):
        payload = request.httprequest.data.decode()
        payload = json.loads(payload)

        discussion_id = payload.get('DISCUSSION_ID')
        if not discussion_id:
            return json.dumps({"error": "Discussion ID Not found"})

        api_key = payload.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = payload.get('MEMBERSHIP_ID')
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})

        document = payload.get('document')
        comment = payload.get('comment')
        discussion_id = request.env['discussion.forum'].sudo().search([('id', '=', discussion_id)], limit=1)
        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        if member:
            create_discussion_comment = request.env['discussion.comment'].sudo().create({
                'member_id': member.id or False,
                'discussion_id': discussion_id.id or False,
                'document': document or '',
            })
            if document:
                document = document.replace(" ", "+")
                create_discussion_comment.write({'image': document})
            if comment:
                create_discussion_comment.write({'comment': comment})
            return json.dumps({'Discussion': 'comment_created', 'Comment ID': create_discussion_comment.id})
        else:
            return json.dumps({"error": "Membership ID is mismatched"})

    @http.route('/update/discussion_comment/json', type="json", auth='none', methods=['POST'], csrf=False)
    def action_update_discussion_comment_json(self, **kw):
        payload = request.httprequest.data.decode()
        payload = json.loads(payload)

        comment_id = payload.get('COMMENT_ID')
        api_key = payload.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = payload.get('MEMBERSHIP_ID')
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})

        comment = payload.get('comment')
        document = payload.get('document')
        membership_no = payload.get('membership_no')

        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        update_member = request.env['res.member'].sudo().search([('membership_no', '=', membership_no)], limit=1)
        if member:
            discussion_comment = request.env['discussion.comment'].sudo().search(
                [('id', '=', comment_id)], limit=1)
            if discussion_comment:
                update_comment = discussion_comment.sudo().write({
                    'member_id': update_member.id or member.id,
                    'document': document or '',
                })
                if document:
                    document = document.replace(" ", "+")
                    discussion_comment.write({'image': document})
                if comment:
                    discussion_comment.write({'comment': comment})
                return json.dumps({'comment': 'comment_updated', 'Discussion Comment ID': discussion_comment.id})
            else:
                return json.dumps({'error': 'Id is not Mismatched'})
        else:
            return json.dumps({"error": "Membership ID is mismatched"})

    @http.route('/update/discussion_comment', type='http', auth='none', methods=['POST'], csrf=False)
    def action_update_discussion_comment(self, **kw):
        comment_id = kw.get('COMMENT_ID')
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        data = kw.get('data')
        data = data.replace("'", '"')
        data_dict = json.loads(data)
        comment = data_dict.get('comment')
        document = data_dict.get('document')
        membership_no = data_dict.get('membership_no')

        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        update_member = request.env['res.member'].sudo().search([('membership_no', '=', membership_no)], limit=1)
        if member:
            discussion_comment = request.env['discussion.comment'].sudo().search(
                [('id', '=', comment_id)], limit=1)
            if discussion_comment:
                update_comment = discussion_comment.sudo().write({
                    'member_id': update_member.id or member.id,
                    'document': document or '',
                })
                if document:
                    document = document.replace(" ", "+")
                    discussion_comment.write({'image': document})
                if comment:
                    discussion_comment.write({'comment': comment})
                return json.dumps({'comment': 'comment_updated', 'Discussion Comment ID': discussion_comment.id})
            else:
                return json.dumps({'error': 'Id is not Mismatched'})
        else:
            return json.dumps({"error": "Membership ID is mismatched"})

    @http.route('/create/child/discussion_comment', type='http', auth='none', methods=['POST'], csrf=False)
    def action_create_child_discussion_comment(self, **kw):
        discussion_id = kw.get('DISCUSSION_ID')
        if not discussion_id:
            return json.dumps({"error": "Discussion ID Not found"})

        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        data = kw.get('data')
        data = data.replace("'", '"')
        data_dict = json.loads(data)
        document = data_dict.get('document')
        comment = data_dict.get('comment')
        parent_comment_id = data_dict.get('parent_comment_id')
        discussion_id = request.env['discussion.forum'].sudo().search([('id', '=', discussion_id)], limit=1)
        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        comment_id = request.env['discussion.comment'].sudo().search([('id', '=', int(parent_comment_id))], limit=1)
        if member:
            create_discussion_child_comment = request.env['child.discussion.comment'].sudo().create({
                'member_id': member.id or False,
                'discussion_id': discussion_id.id or False,
                'document': document or '',
                'comment_id': comment_id.id or False,
            })
            if document:
                document = document.replace(" ", "+")
                create_discussion_child_comment.write({'image': document})
            if comment:
                create_discussion_child_comment.write({'comment': comment})
            return json.dumps({'Discussion': 'child comment_created', 'Child Comment ID': create_discussion_child_comment.id})
        else:
            return json.dumps({"error": "Membership ID is mismatched"})

    @http.route('/update/child/discussion_comment', type='http', auth='none', methods=['POST'], csrf=False)
    def action_update_child_discussion_comment(self, **kw):
        comment_id = kw.get('COMMENT_ID')
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        data = kw.get('data')
        data = data.replace("'", '"')
        data_dict = json.loads(data)
        comment = data_dict.get('comment')
        document = data_dict.get('document')
        membership_no = data_dict.get('membership_no')
        child_comment_id = data_dict.get('child_comment_id')

        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        update_member = request.env['res.member'].sudo().search([('membership_no', '=', membership_no)], limit=1)
        if member:
            child_discussion_comment = request.env['child.discussion.comment'].sudo().search(
                [('id', '=', child_comment_id)], limit=1)
            if child_discussion_comment:
                update_comment = child_discussion_comment.sudo().write({
                    'member_id': update_member.id or member.id,
                    'document': document or '',
                })
                if document:
                    document = document.replace(" ", "+")
                    child_discussion_comment.write({'image': document})
                if comment:
                    child_discussion_comment.write({'comment': comment})
                return json.dumps({'comment': 'comment_updated', 'Child Comment ID': child_discussion_comment.id})
            else:
                return json.dumps({'error': 'Id is not Mismatched'})
        else:
            return json.dumps({"error": "Membership ID is mismatched"})

    @http.route('/delete/discussion', type='http', auth='none', methods=['DELETE'], csrf=False)
    def action_delete_discussion_comment(self, **kw):
        api_key = kw.get('api_key')
        comment_id = kw.get('COMMENT_ID')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})

        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        if member:
            discussion_comment = request.env['discussion.comment'].sudo().search(
                [('member_id', '=', member.id), ('id', '=', comment_id)], limit=1)
            if discussion_comment:
                discussion_comment.sudo().unlink()
                return json.dumps({'comment': 'comment_deleted'})
            else:
                return json.dumps({'error': "Record not found"})

        else:
            return json.dumps({"error": "Membership ID is mismatched"})
