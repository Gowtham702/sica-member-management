import base64
from odoo import http, fields
from odoo.http import request
import json
import random
import requests
import datetime
from datetime import datetime
import razorpay
import base64
import io

print("CUSTOM MAIN CONTROLLER LOADED")

class UpdateResMasterDetails(http.Controller):
    @http.route('/post/member_details', type='http', auth='none', methods=['POST'], csrf=False)
    def post_member_details(self, **kw):

        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')  # Corrected case for 'membership_id'

        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})

        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})

        data = kw.get('data')
        data = data.replace("'", '"')
        data_dict = json.loads(data)
        name = data_dict.get('member_name') or ''
        contact1 = data_dict.get('mobile_number') or ''
        email = data_dict.get('email') or ''
        skills = data_dict.get('skills') or ''
        medium = data_dict.get('medium') or ''
        experience = data_dict.get('experience') or ''
        portifolio_link = data_dict.get('portifolio_link') or ''
        designation = data_dict.get('designation') or ''
        membership_no = data_dict.get('membership_no') or ''
        profile_photo_data = data_dict.get('profile_photo_data') or ''
        contact_privacy = data_dict.get('show_contact') or ''
        if contact_privacy == 'True':
            contact_privacy = True
        else:
            contact_privacy = False

        notes_privacy = data_dict.get('show_notes') or ''
        if notes_privacy == 'True':
            notes_privacy = True
        else:
            notes_privacy = False
        if membership_no == '':
            return json.dumps({"error": "Membership ID is mismatched"})
        notes = data_dict.get('notes') or ''
        medium_id = request.env['member.medium'].sudo().search([('name', '=', medium)], limit=1)
        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        check_member = request.env['res.member'].sudo().search(
            [('membership_no', '=', membership_no), ('id', '!=', member.id)], limit=1)
        if check_member:
            return json.dumps({'error': "Membership Number is Wrong"})
        if member:
            member.write({'name': name,
                          'contact1': contact1,
                          'skills': skills,
                          'medium_id': medium_id.id,
                          'experience': experience,
                          'portifolio_link': portifolio_link,
                          'designation': designation,
                          'membership_no': membership_no,
                          'notes': notes,
                          'profile_photo_data': profile_photo_data,
                          'contact_privacy': contact_privacy,
                          'notes_privacy': notes_privacy,
                          'email' : email,
                          })
            return json.dumps({'membership': 'Details Updated'})
        else:
            return json.dumps({"error": "Membership ID is mismatched"})


class UpdateResMasterSocialDetails(http.Controller):
    @http.route('/post/member_social_links', type='http', auth='none', methods=['POST'], csrf=False)
    def post_member_social_link_details(self, **kw):

        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')  # Corrected case for 'membership_id'

        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})

        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})

        youtube_link = kw.get('youtube_link') or ''
        facebook_link = kw.get('facebook_link') or ''
        instagram_link = kw.get('instagram_link') or ''
        linkedin_link = kw.get('linkedin_link') or ''
        other_link = kw.get('other_link') or ''
        vimeo_link = kw.get('vimeo_link') or ''
        twitter_link = kw.get('twitter_link') or ''
        imdb_link = kw.get('imdb_link') or ''

        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        if member:
            member.write({'youtube_link': youtube_link})
            member.write({'facebook_link': facebook_link})
            member.write({'instagram_link': instagram_link})
            member.write({'linkedin_link': linkedin_link})
            member.write({'other_link': other_link})
            member.write({'vimeo_link': vimeo_link})
            member.write({'twitter_link': twitter_link})
            member.write({'imdb_link': imdb_link})
            return json.dumps({'membership': 'Social Link Updated'})
        else:
            return json.dumps({"error": "Membership ID is mismatched"})


class MemberDetails(http.Controller):
    @http.route('/get/member_details', type='http', auth='none', methods=['GET'], csrf=False)
    def get_member_details(self, **kw):
        base_url = request.env['ir.config_parameter'].sudo().get_param(
            'web.base.url.image'
        ) or request.env['ir.config_parameter'].sudo().get_param(
            'web.base.url'
        )

        base_url = base_url.rstrip('/')

        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')  # Corrected case for 'membership_id'

        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})

        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})

        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        if not member:
            return json.dumps({"error": "Membership Not Valid"})
        image = ''
        if member.image_1920:
            image = '%s/get/public/image/%s/%s/%s' % (
                base_url,
                member._name,
                member.id,
                'image_1920'
            )
        state_value = member.state

        status_for_value = next((label for value, label in member._fields['state'].selection if value == state_value),
                               None)
        status_value = status_for_value.capitalize()
        general_vals = {
            'name': member.name,
            'designation': member.designation or '',
            'membership_no': member.membership_no or '',
            'joining_date': member.date_of_join.strftime("%Y-%m-%d") if member.date_of_join else '',
            'date_of_birth': member.dob.strftime("%Y-%m-%d") if member.dob else '',
            'subscription_end_date': member.subscription_end_date.strftime(
                "%Y-%m-%d") if member.subscription_end_date else '',
            'skills': member.skills or '',
            'medium_id': member.medium_id.id,
            'medium_name': member.medium_id.name,
            'portifolio_link': member.portifolio_link or '',  # Corrected typo in 'portfolio_link'
            'notes': member.notes or '',
            'mobile_number': member.contact1 or '',
            'experience': member.experience or '',
            'grade': member.grade.capitalize() or '',
            'state': status_value or '',
            'facebook_link': member.facebook_link or '',
            'instagram_link': member.instagram_link or '',
            'youtube_link': member.youtube_link or '',
            'twitter_link': member.twitter_link or '',
            'linkedin_link': member.linkedin_link or '',
            'vimeo_link': member.vimeo_link or '',
            'other_link': member.other_link or '',
            'show_social_link': member.show_social_link or '',
            'show_discussion': member.show_discussion or '',
            'show_all_members': member.show_all_members or '',
            'show_all_works': member.show_all_works or '',
            'show_job_seeker': member.show_job_seeker or '',
            'show_job_provider': member.show_job_provider or '',
            'image': image or '',
            'sica_amount': member.sica_fee,
            'cbt_fee': member.cbt_fee,
            'paid_till': member.paid_till,
            'email': member.email,
            'contact_privacy': member.contact_privacy,
            'notes_privacy': member.notes_privacy,
            'gender': member.gender,
            'lcf': member.lcf,
            'loans': member.loans,
            'aids': member.aids,
            'cam_life': member.cam_life,
            'expired_date': member.expired_date.strftime("%Y-%m-%d") if member.expired_date else '',
            'show_grievance_forum': member.show_grievance_forum,
            'show_shooting': member.show_shooting,
            'show_shooting_dop': member.show_shooting_dop,
            'imdb_link': member.imdb_link,
            'fefsi_card': member.fefsi_card,
        }

        work_vals = []
        for work in member.work_ids:
            # image = base_url + '/web/image?' + 'model=member.work&id=' + str(work.id) + '&field=image'
            image = '%s/get/public/image/%s/%s/%s' % (
                base_url,
                work._name,
                work.id,
                'image'
            ) if work.image else ''
            work_vals.append({
                'project_name': work.project_name or '',
                'designation': work.designation or '',
                'year': work.year or '',
                'id': work.id or False,
                'format': work.format or '',
                'dop_name': work.dop_name or '',
                'image': str(image) or '',
                'weblink': work.weblink or '',
                'language': work.language or '',
                'approval_status': work.approve_status or '',
            })

        discussion_form = []
        topics = []
        own_topic_ids = request.env['discussion.forum'].sudo().search([('member_id', '=', member.id)])
        for discussion in own_topic_ids:
            image = '%s/get/public/image/%s/%s/%s' % (
                base_url,
                member._name,
                member.id,
                'image_1920'
            )
            discussion_vals = {
                'profile': image or '',
                'topic': discussion.discussion_topic,
                'member_name': discussion.member_id.name,
                'category_name': discussion.category_id.name,
                'category_id': discussion.category_id.id,
                'discussion_id': discussion.id,
                'create_date': discussion.create_date.strftime("%Y-%m-%d %H:%M:%S") if discussion.create_date else '',
                'member_id': discussion.member_id.id,
                'designation': discussion.member_id.designation,
            }
            topics.append(discussion)
            print(discussion.name)
            discussion_comment_vals = []
            for comment in discussion.discussion_comment_ids:
                profile_image = '%s/get/public/image/%s/%s/%s' % (
                    base_url,
                    comment.member_id._name,
                    comment.member_id.id,
                    'image_1920'
                )
                discussion_comment_vals.append({
                    'profile_image': profile_image or '',
                    'comment': comment.comment or '',
                    'comment_create_date': comment.create_date.strftime(
                        "%Y-%m-%d %H:%M:%S") if comment.create_date else '',
                    'member_name': comment.member_id.name or '',
                    'designation': comment.member_id.designation,
                    'comment_id': comment.id,
                })

            discussion_form.append(
                {'topic': discussion_vals, 'discussion_comments': discussion_comment_vals})

        user_comment_topic_ids = request.env['discussion.comment'].sudo().search([('member_id', '=', member.id)])
        topis = user_comment_topic_ids.discussion_id
        for user_discussion in topis:
            if user_discussion not in topics:
                image = '%s/get/public/image/%s/%s/%s' % (
                    base_url,
                    user_discussion.member_id._name,
                    user_discussion.member_id.id,
                    'image_1920'
                )
                discussion_vals = {
                    'profile': image or '',
                    'topic': user_discussion.discussion_topic,
                    'member_name': user_discussion.member_id.name,
                    'category_name': user_discussion.category_id.name,
                    'category_id': user_discussion.category_id.id,
                    'discussion_id': user_discussion.id,
                    'create_date': user_discussion.create_date.strftime("%Y-%m-%d %H:%M:%S") if user_discussion.create_date else '',
                    'member_id': user_discussion.member_id.id,
                    'designation': user_discussion.member_id.designation,
                }
                print(user_discussion.name)
                topics.append(user_discussion)
                discussion_comment_vals = []
                for comment in user_discussion.discussion_comment_ids:
                    if comment.member_id.id == member.id:
                        profile_image = '%s/get/public/image/%s/%s/%s' % (
                            base_url,
                            comment.member_id._name,
                            comment.member_id.id,
                            'image_1920'
                        )
                        discussion_comment_vals.append({
                            'profile_image': profile_image or '',
                            'comment': comment.comment or '',
                            'comment_create_date': comment.create_date.strftime(
                                "%Y-%m-%d %H:%M:%S") if comment.create_date else '',
                            'member_name': comment.member_id.name or '',
                            'designation': comment.member_id.designation,
                            'comment_id': comment.id,
                        })
                    discussion_form.append(
                        {'topic': discussion_vals, 'discussion_comments': discussion_comment_vals})

        return json.dumps({'member_basic_details': general_vals, 'project_work': work_vals, 'discussion_forum': discussion_form})

    @http.route('/get/all/member_details', type='http', auth='none', methods=['GET'], csrf=False)
    def get_all_member_details(self, **kw):
        base_url = request.env['ir.config_parameter'].sudo().get_param(
            'web.base.url.image'
        ) or request.env['ir.config_parameter'].sudo().get_param(
            'web.base.url'
        )

        base_url = base_url.rstrip('/')

        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        offset = int(kw.get('offset'))
        limit = int(kw.get('limit'))
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        member_ids = request.env['res.member'].sudo().search([], offset=offset, limit=limit)
        members_details = []
        for member in member_ids:
            state_value = member.state

            status_for_value = next(
                (label for value, label in member._fields['state'].selection if value == state_value),
                None)
            image = ''
            if member.image_1920:
                image = '%s/get/public/image/%s/%s/%s' % (
                    base_url,
                     member._name,
                     member.id,
                    'image_1920'
                )
            member_vals = {
                'name': member.name,
                'id': member.id,
                'screen_name': member.alias_name or '',
                'designation': member.designation or '',
                'membership_no': member.membership_no or '',
                'joining_date': member.date_of_join.strftime("%Y-%m-%d") if member.date_of_join else '',
                'skills': member.skills or '',
                'grade': member.grade.capitalize() or '',
                'state': status_for_value or '',
                'date_of_birth': member.dob.strftime("%Y-%m-%d") if member.dob else '',
                'medium': member.medium or '',
                'portifolio_link': member.portifolio_link or '',  # Corrected typo in 'portfolio_link'
                'notes': member.notes or '',
                'medium_id': member.medium_id.id,
                'medium_name': member.medium_id.name,
                'mobile_number': member.contact1 or '',
                'experience': member.experience or '',
                'facebook_link': member.facebook_link or '',
                'instagram_link': member.instagram_link or '',
                'youtube_link': member.youtube_link or '',
                'twitter_link': member.twitter_link or '',
                'linkedin_link': member.linkedin_link or '',
                'vimeo_link': member.vimeo_link or '',
                'other_link': member.other_link or '',
                'image': image or '',
                'show_discussion': member.show_discussion,
                'show_all_members': member.show_all_members,
                'show_all_works': member.show_all_works,
                'show_job_seeker': member.show_job_seeker,
                'show_job_provider': member.show_job_provider,
                'email': member.email,
                'contact_privacy': member.contact_privacy,
                'notes_privacy': member.notes_privacy,
                'gender': member.gender,
                'lcf': member.lcf,
                'loans': member.loans,
                'aids': member.aids,
                'cam_life': member.cam_life,
                'expired_date': member.expired_date.strftime("%Y-%m-%d") if member.expired_date else '',
                'show_grievance_forum': member.show_grievance_forum,
                'show_shooting': member.show_shooting,
                'show_shooting_dop': member.show_shooting_dop,
                'imdb_link': member.imdb_link,
                'fefsi_card': member.fefsi_card,
            }
            work_vals = []
            for work in member.work_ids:
                image = '%s/get/public/image/%s/%s/%s' % (
                    base_url,
                    work._name,
                    work.id,
                    'image'
                ) if work.image else ''
                work_vals.append({
                    'project_name': work.project_name or '',
                    'designation': work.designation or '',
                    'year': work.year or '',
                    'id': work.id,
                    'format': work.format or '',
                    'weblink': work.weblink or '',
                    'language': work.language or '',
                })
            members_details.append({'member_details': member_vals, 'works': work_vals})
        return json.dumps({'member_basic_details': members_details})

    @http.route('/get/mobile_photo', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_mobile_photo(self, **kw):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url.image').rstrip('/')
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        photo_list = []
        for mobile_photo in request.env['mobile.photo'].sudo().search([('photo', '!=', False)]):
            image_url = base_url + '/get/public/image/mobile.photo/' + str(mobile_photo.id) + '/photo'
            vals = {}
            vals['name'] = mobile_photo.name or ''
            vals['promotion_link'] = mobile_photo.promotion_link or ''
            vals['image_url'] = image_url or ''
            vals['image'] = mobile_photo.photo.decode('utf-8') if mobile_photo.photo else ''
            photo_list.append(vals)
        return json.dumps({'photo': photo_list})

    @http.route('/get/public/image/<string:model>/<int:record_id>/<string:field>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_public_image(self, model, record_id, field, **kw):
        record = request.env[model].sudo().browse(record_id)

        if not record.exists():
            return request.not_found()

        image_data = record[field]

        if not image_data:
            return request.not_found()

        image_binary = base64.b64decode(image_data)

        headers = [
            ('Content-Type', 'image/jpeg'),
            ('Content-Length', str(len(image_binary)))
        ]

        return request.make_response(image_binary, headers=headers)

    @http.route('/get/all/medium', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_all_medium(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        medium_ids = request.env['member.medium'].sudo().search([])
        reason_details = []
        for medium in medium_ids:
            reason_details.append({
                'format_name': medium.name,
                'format_id': medium.id
            })
        return json.dumps({'medium_details': reason_details})



class AuthoticationCheck(http.Controller):
    @http.route('/check_api', type='http', auth='public', methods=['GET'])
    def check_api_key(self, **kw):
        api_key = kw.get('api_key')
        if api_key:
            url = 'http://localhost:8055'
            response = requests.get(url, headers={'Authorization': f'Bearer {api_key}'})

            if response.ok:
                # response.ok checks for 2xx status codes which generally indicate success
                print("Request successful")
                # Process the response data here
            else:
                if response.status_code == 401:
                    print("Unauthorized - API key might be invalid or lacks necessary permissions")
                else:
                    print(f"Request failed with status code {response.status_code}: {response.text}")
                    
class ImageAPIController(http.Controller):

    @http.route('/api/member_image', type='http', auth='public', methods=['GET'], csrf=False)
    def get_member_image(self, **kw):
        member_id = kw.get('member_id')

        if not member_id:
            return request.not_found()

        member = request.env['res.member'].sudo().browse(int(member_id))

        if not member.exists() or not member.image_1920:
            return request.not_found()

        image_binary = base64.b64decode(member.image_1920)

        return request.make_response(
            image_binary,
            headers=[('Content-Type', 'image/png')]
        )
    @http.route('/post/member/status', type='http', auth='none', methods=['POST'], csrf=False)
    def post_member_status(self, **kw):
        api_key = kw.get('api_key')
        if api_key != API_KEY:
            return json.dumps({"error": "Invalid API key"})

        member_id = kw.get('member_id')
        caption = kw.get('caption') or ''
        media_file = kw.get('media_file')
        media_filename = kw.get('media_filename') or 'status_file'
        media_type = kw.get('media_type') or 'image'

        member = request.env['res.member'].sudo().browse(int(member_id))

        if not member.exists():
            return json.dumps({"error": "Member not found"})

        status = request.env['member.status'].sudo().create({
            'member_id': member.id,
            'caption': caption,
            'media_file': media_file,
            'media_filename': media_filename,
            'media_type': media_type,
        })

        return json.dumps({
            "success": True,
            "status_id": status.id
        })
    
    @http.route('/get/member/status', type='http', auth='none', methods=['GET'], csrf=False)
    def get_member_status(self, **kw):
        api_key = kw.get('api_key')
        if api_key != API_KEY:
            return json.dumps({"error": "Invalid API key"})

        base_url = get_base_url()

        statuses = request.env['member.status'].sudo().search([
            ('expiry_time', '>=', fields.Datetime.now()),
            ('media_file', '!=', False)
        ])

        result = []

        for status in statuses:
            media_url = '%s/web/content?model=member.status&id=%s&field=media_file&filename=%s' % (
                base_url,
                status.id,
                status.media_filename or 'status_file'
            )

            result.append({
                'status_id': status.id,
                'member_id': status.member_id.id,
                'member_name': status.member_id.name,
                'caption': status.caption or '',
                'media_type': status.media_type,
                'media_url': media_url,
                'expiry_time': str(status.expiry_time),
            })

        return json.dumps({
            'statuses': result
        })

# class ResPartnerController(http.Controller):
#     @http.route('/custom_api/get_res_partners', type='http', auth='public', methods=['GET'])
#     def get_res_partners_id(self, **kw):
#         partner_records = request.env['res.partner'].sudo().search_read([], ['name', 'email', 'phone'])
#         return json.dumps(partner_records)
#
# class LoginOtpRequest(http.Controller):
#
#     @http.route('/api/get_login_otp', type='http', auth='none', methods=['GET'])
#     def get_res_partners(self, **kw):
#         api_key = kw.get('api_key')  # Extract the API key from the GET parameters
#         stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
#         mobile_number = kw.get('MOBILE_NUMBER')
#         membership_id = kw.get('MEMBERSHIP_ID')
#         if api_key != stored_api_key:
#             return json.dumps({"error": "Invalid API key"})
#         account_type = kw.get('account_type')
#         if not account_type:
#             create_otp_master = request.env['sms.otp'].create({
#                 'account_type': 'member',
#                 'otp_number': '',
#                 'mobile_number': mobile_number,
#                 'membership_number': membership_id,
#                 'return_value': 'ACCOUNT TYPE MISSING',
#             })
#             return json.dumps({'error': 'ACCOUNT TYPE MISSING'})
#         otp_length = 4
#         # Generate a random OTP
#         otp = ""
#         for i in range(otp_length):
#             otp += str(random.randint(0, 4))
#         if account_type == 'GUEST':
#             mobile_number = kw.get('MOBILE_NUMBER')
#             if not mobile_number:
#                 create_otp_master = request.env['sms.otp'].create({
#                     'account_type': 'guest',
#                     'otp_number': '',
#                     'mobile_number': mobile_number,
#                     'membership_number': membership_id,
#                     'return_value': 'MOBILE NUMBER IS REQUIRED',
#                 })
#
#                 return json.dumps({'error': 'MOBILE NUMBER IS REQUIRED'})
#             post_url = "http://pay4sms.in/sendsms/?token=83ba323c7d09c429d81666aaacb224bb&credit=2&sender=SICAMS&message=Dear%20Member,%20your%20OTP%20for%20SICA%20App%20registration%20is%20{}.%20Please%20do%20not%20share%20it%20with%20anyone.&number={}".format(
#                 otp,mobile_number)
#             post_result = requests.post(post_url)
#             if post_result.status_code == 200:  # Assuming a successful response
#                 post_return = post_result.text
#                 if ':' in post_return:
#                     create_otp_master = request.env['sms.otp'].create({
#                         'account_type': 'guest',
#                         'otp_number': '',
#                         'mobile_number': mobile_number,
#                         'membership_number': membership_id,
#                         'return_value': post_return,
#                     })
#                     return json.dumps({'error': post_return})
#                 post_return_list = json.loads(post_return)
#                 second_value = post_return_list[0][1]
#                 get_url = "http://pay4sms.in/Dlrcheck/?token=83ba323c7d09c429d81666aaacb224bb&msgid={}".format(
#                     second_value)
#                 get_result = requests.get(get_url)
#                 if get_result.status_code == 200:
#                     create_otp_master = request.env['sms.otp'].create({
#                         'account_type': 'guest',
#                         'otp_number': otp,
#                         'mobile_number': mobile_number,
#                         'membership_number': membership_id,
#                         'return_value': get_result.text,
#                     })
#                     return json.dumps({'account_type': 'GUEST', 'OTP': otp})
#                 else:
#                     create_otp_master = request.env['sms.otp'].create({
#                         'account_type': 'guest',
#                         'otp_number': otp,
#                         'mobile_number': mobile_number,
#                         'membership_number': membership_id,
#                         'return_value': get_result.status_code,
#                     })
#                     return json.dumps({'error': get_result.status_code})
#             else:
#                 create_otp_master = request.env['sms.otp'].create({
#                     'account_type': 'guest',
#                     'otp_number': otp,
#                     'mobile_number': mobile_number,
#                     'membership_number': membership_id,
#                     'return_value': post_result.status_code,
#                 })
#                 return json.dumps({'error': post_result.status_code})
#
#         if account_type == 'MEMBER':
#             membership_id = kw.get('MEMBERSHIP_ID')
#             if not membership_id:
#                 create_otp_master = request.env['sms.otp'].create({
#                     'account_type': 'member',
#                     'otp_number': otp,
#                     'membership_number': membership_id,
#                     'return_value': 'MEMBERSHIP IS REQUIRED'
#                 })
#                 return json.dumps({'error': 'MEMBERSHIP IS REQUIRED'})
#             mobile_number = kw.get('MOBILE_NUMBER')
#             if not mobile_number:
#                 create_otp_master = request.env['sms.otp'].create({
#                     'account_type': 'member',
#                     'otp_number': otp,
#                     'mobile_number': mobile_number,
#                     'membership_number': membership_id,
#                     'return_value': 'MOBILE NUMBER IS REQUIRED'
#                 })
#                 return json.dumps({'error': 'MOBILE NUMBER IS REQUIRED'})
#             member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
#             if member:
#                 membership_number = request.env['res.member'].sudo().search([('id', '=', member.id), '|', ('contact1', '=', mobile_number), ('contact2', '=', mobile_number)], limit=1)
#                 if not membership_number:
#                     create_otp_master = request.env['sms.otp'].create({
#                         'account_type': 'member',
#                         'otp_number': otp,
#                         'mobile_number': mobile_number,
#                         'membership_number': membership_id,
#                         'return_value': 'MOBILE NUMBER IS MISMATCHED'
#                     })
#                     return json.dumps({'error': 'MOBILE NUMBER IS MISMATCHED'})
#             else:
#                 create_otp_master = request.env['sms.otp'].create({
#                     'account_type': 'member',
#                     'otp_number': otp,
#                     'mobile_number': mobile_number,
#                     'membership_number': membership_id,
#                     'return_value': 'MEMBERSHIP ID IS MISSING OR WRONG'
#                 })
#                 return json.dumps({'error': 'MEMBERSHIP ID IS MISSING OR WRONG'})
#             post_url = "http://pay4sms.in/sendsms/?token=83ba323c7d09c429d81666aaacb224bb&credit=2&sender=SICAMS&message=Dear%20Member,%20your%20OTP%20for%20SICA%20App%20registration%20is%20{}.%20Please%20do%20not%20share%20it%20with%20anyone.&number={}".format(
#                 otp, mobile_number)
#             post_result = requests.post(post_url)
#             if post_result.status_code == 200:  # Assuming a successful response
#                 post_return = post_result.text
#                 if ':' in post_return:
#                     create_otp_master = request.env['sms.otp'].create({
#                         'member_id': member.id,
#                         'account_type': 'member',
#                         'otp_number': otp,
#                         'membership_number': membership_id,
#                         'mobile_number': mobile_number,
#                         'return_value': post_return
#                     })
#                     return json.dumps({'error': post_return})
#                 post_return_list = json.loads(post_return)
#                 second_value = post_return_list[0][1]
#                 get_url = "http://pay4sms.in/Dlrcheck/?token=83ba323c7d09c429d81666aaacb224bb&msgid={}".format(
#                     second_value)
#                 get_result = requests.get(get_url)
#                 if get_result.status_code == 200:
#                     create_otp_master = request.env['sms.otp'].create({
#                         'member_id': member.id,
#                         'account_type': 'member',
#                         'otp_number': otp,
#                         'membership_number': membership_id,
#                         'mobile_number': mobile_number,
#                         'return_value': get_result.json()
#                     })
#                     return json.dumps({'account_type': 'MEMBER', 'OTP': otp})
#                 else:
#                     create_otp_master = request.env['sms.otp'].create({
#                         'member_id': member.id,
#                         'account_type': 'member',
#                         'otp_number': otp,
#                         'membership_number': membership_id,
#                         'mobile_number': mobile_number,
#                         'return_value': get_result.json()
#                     })
#                     return json.dumps({'error': get_result.status_code})
#             else:
#                 create_otp_master = request.env['sms.otp'].create({
#                     'member_id': member.id,
#                     'account_type': 'member',
#                     'otp_number': otp,
#                     'mobile_number': mobile_number,
#                     'membership_number': membership_id,
#                     'return_value': post_result.status_code
#                 })
#                 return json.dumps({'error': post_result.status_code})

