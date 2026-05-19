from odoo import http, fields
from odoo.http import request
import json
import random
import requests
import datetime
from datetime import datetime
import razorpay
import logging

_logger = logging.getLogger(__name__)


class CreateJOb(http.Controller):
    @http.route('/get/skills', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_skills(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')  # Corrected case for 'membership_id'

        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})

        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        skill_ids = request.env['member.skill'].sudo().search([])
        skills = []
        for skill in skill_ids:
            skills.append({
                'skill': skill.name,
                'id': skill.id
            })

        return json.dumps({'Skills': skills})

    @http.route('/get/job_post', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_job_post(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')  # Corrected case for 'membership_id'

        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})

        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        job_title_ids = request.env['job.title'].sudo().search([])
        job_post_vals = []
        for job_post in job_title_ids:
            job_post_vals.append({
                'post': job_post.name,
                'id': job_post.id
            })

        return json.dumps({'Job Post': job_post_vals})

    @http.route('/create/job_seeker/json', type="json", auth='none', methods=['POST'], csrf=False)
    def action_create_job_seeker_json(self, **kw):

        payload = request.httprequest.data.decode()
        payload = json.loads(payload)

        api_key = payload.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = payload.get('MEMBERSHIP_ID')  # Corrected case for 'membership_id'

        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})

        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})

        mobile_number = payload.get('mobile_number') or ''
        membership_no = payload.get('membership_no') or ''
        member_name = payload.get('member_name') or ''
        note = payload.get('note') or ''
        portifolio_link = payload.get('portifolio_link') or ''
        portifolio_link_2 = payload.get('portifolio_link_2') or ''
        document_binary = payload.get('document_binary') or ''
        availability_from = payload.get('availability_from') or ''
        availability_till = payload.get('availability_till') or ''
        skills = payload.get('skills') or ''
        medium = payload.get('format_id') or ''
        grade = payload.get('grade') or ''
        skill_list = skills.split(', ')

        skill_ids = []
        for skill in skill_list:
            skill_id = request.env['member.skill'].sudo().search([('name', '=', skill)], limit=1)
            if skill_id:
                skill_ids.append(skill_id.id)
        medium_ids = False
        if medium:
            medium_id = request.env['member.medium'].sudo().search([('id', '=', int(medium))], limit=1)
            if medium:
                medium_ids = medium_id.id
        date_format = "%d/%m/%Y"
        if availability_from == "":
            availability_from = None
        else:
            availability_from = datetime.strptime(availability_from, date_format).date()
        if availability_till == "":
            availability_till = None
        else:
            availability_till = datetime.strptime(availability_till, date_format).date()
        if membership_id == '':
            return json.dumps({"error": "Membership ID is mismatched"})
        post_apply = payload.get('post_apply') or ''
        post_applies = False
        if post_apply:
            job_title = request.env['job.title'].sudo().search([('name', '=', post_apply)], limit=1)
            if job_title:
                post_applies = job_title.id
            else:
                job_title = request.env['job.title'].sudo().create({'name': post_apply})
                post_applies = job_title.id

        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        job_seeker = request.env['member.job.seeker'].sudo().create({'mobile_number': mobile_number,
                                                                     'membership_no': membership_no,
                                                                     'member_id': member.id,
                                                                     'portifolio_link': portifolio_link,
                                                                     'portifolio_link_2': portifolio_link_2,
                                                                     'member_name': member_name,
                                                                     'skill_ids': [(6, 0, skill_ids)],
                                                                     'post_applying_id': post_applies,
                                                                     'medium_id': medium_ids,
                                                                     'grade': grade,
                                                                     # 'available_date': available_date.strftime("%d/%m/%Y") if available_date and isinstance(available_date, datetime.date) else None,
                                                                     'start_date': availability_from,
                                                                     'till_date': availability_till,
                                                                     'note': note,
                                                                     'document': document_binary
                                                                     })
        return json.dumps({'membership': 'Job seeker Created', 'ID': job_seeker.id})


    @http.route('/create/job_seeker', type='http', auth='none', methods=['POST'], csrf=False)
    def action_create_job_seeker(self, **kw):

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
        mobile_number = data_dict.get('mobile_number') or ''
        membership_no = data_dict.get('membership_no') or ''
        member_name = data_dict.get('member_name') or ''
        note = data_dict.get('note') or ''
        portifolio_link = data_dict.get('portifolio_link') or ''
        portifolio_link_2 = data_dict.get('portifolio_link_2') or ''
        document_binary = data_dict.get('document_binary') or ''
        availability_from = data_dict.get('availability_from') or ''
        availability_till = data_dict.get('availability_till') or ''
        skills = data_dict.get('skills') or ''
        medium = data_dict.get('format_id') or ''
        grade = data_dict.get('grade') or ''
        skill_list = skills.split(', ')
        skill_ids = []
        for skill in skill_list:
            skill_id = request.env['member.skill'].sudo().search([('name', '=', skill)], limit=1)
            if skill_id:
                skill_ids.append(skill_id.id)
        medium_ids = False
        if medium:
            medium_id = request.env['member.medium'].sudo().search([('id', '=', int(medium))], limit=1)
            if medium:
                medium_ids = medium_id.id
        date_format = "%d/%m/%Y"
        if availability_from == "":
            availability_from = None
        else:
            availability_from = datetime.strptime(availability_from, date_format).date()
        if availability_till == "":
            availability_till = None
        else:
            availability_till = datetime.strptime(availability_till, date_format).date()
        if membership_id == '':
            return json.dumps({"error": "Membership ID is mismatched"})
        post_apply = data_dict.get('post_apply') or ''
        post_applies = False
        if post_apply:
            job_title = request.env['job.title'].sudo().search([('name', '=', post_apply)], limit=1)
            if job_title:
                post_applies = job_title.id
            else:
                job_title = request.env['job.title'].sudo().create({'name': post_apply})
                post_applies = job_title.id

        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        job_seeker = request.env['member.job.seeker'].sudo().create({'mobile_number': mobile_number,
                                                                     'membership_no': membership_no,
                                                                     'member_id': member.id,
                                                                     'portifolio_link': portifolio_link,
                                                                     'portifolio_link_2': portifolio_link_2,
                                                                     'member_name': member_name,
                                                                     'skill_ids': [(6, 0, skill_ids)],
                                                                     'post_applying_id': post_applies,
                                                                     'medium_id': medium_ids,
                                                                     'grade': grade,
                                                                     # 'available_date': available_date.strftime("%d/%m/%Y") if available_date and isinstance(available_date, datetime.date) else None,
                                                                     'start_date': availability_from,
                                                                     'till_date': availability_till,
                                                                     'note': note,
                                                                     'document': document_binary
                                                                     })
        job_seeker.send_push_to_job_provider()
        return json.dumps({'membership': 'Job seeker Created', 'ID': job_seeker.id})

    @http.route('/get/member/job_seeker', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_member_job_seeker(self, **kw):

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
        if member:
            job_seeker_vals = []
            job_seeker_ids = request.env['member.job.seeker'].sudo().search([('member_id', '=', member.id)])
            for job_seeker in job_seeker_ids:
                vals = {
                    'membership_no': job_seeker.membership_no or '',
                    'member_id': member.id or False,
                    'portifolio_link': job_seeker.portifolio_link or '',
                    'portifolio_link_2': job_seeker.portifolio_link_2 or '',
                    'member_name': job_seeker.member_name or '',
                    'skill_ids': [{'id': skill.id, 'name': skill.name} for skill in
                                  job_seeker.skill_ids],
                    'post_applying_id': job_seeker.post_applying_id.name or '',
                    'contact1': member.contact1 or '',
                    'contact2': member.contact2 or '',
                    'format_name': job_seeker.medium_id.name or '',
                    'format_id': job_seeker.medium_id.id or '',
                    'grade': job_seeker.grade or '',
                    # 'available_date': available_date.strftime("%d/%m/%Y") if available_date and isinstance(available_date, datetime.date) else None,
                    'start_date': job_seeker.start_date.strftime("%Y-%m-%d") if job_seeker.start_date else '',
                    'till_date': job_seeker.till_date.strftime("%Y-%m-%d") if job_seeker.till_date else '',
                    'note': job_seeker.note,
                    'document_binary': job_seeker.document or '',
                    'job_seeker_id': job_seeker.id
                }
                job_seeker_vals.append(vals)
            return json.dumps({'Member Job Seeker': job_seeker_vals})
    

    # @http.route('/api/job_list/', type='json', auth='none', methods=['GET'], csrf=False)
    # def active_job_list(self, **kw):
    #     try:
    #         api_key = kw.get('api_key')
    #         print(11111111111111111111111111111111111111111111111)
    #         print(api_key)
    #         stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"

    #         if api_key != stored_api_key:
    #             return {
    #                 "status": 403,
    #                 "message": "Invalid API Key"
    #             }

    #         records = request.env['member.job.provider'].sudo().search([('state', '=', 'active')])
    #         result = []
    #         for rec in records:
    #             result.append({
    #                 "id": rec.id,
    #                 "member_name": rec.member_name,
    #                 "mobile_number": rec.mobile_number,
    #                 "designation": rec.designation,
    #                 "experience": rec.experience,
    #                 "skills": [skill.name for skill in rec.skill_ids],
    #                 "project_requirements": [proj.name for proj in rec.project_requirement],
    #                 "available_start_date": rec.available_start_date.strftime('%Y-%m-%d') if rec.available_start_date else None,
    #                 "available_end_date": rec.available_end_date.strftime('%Y-%m-%d') if rec.available_end_date else None,
    #                 "state": rec.state,
    #             })

    #         return {
    #             "status": 200,
    #             "data": result
    #         }

    #     except Exception as e:
    #         return {
    #             "status": 500,
    #             "message": "An error occurred while fetching job list",
    #             "error": str(e)
    #         }

    # @http.route('/post/job_seeker', type='http', auth='none', methods=['POST'], csrf=False)
    # def action_post_job_seeker(self, **kw):

    #     api_key = kw.get('api_key')  # Extract the API key from the GET parameters
    #     stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
    #     membership_id = kw.get('MEMBERSHIP_ID')  # Corrected case for 'membership_id'

    #     if not api_key:
    #         return json.dumps({"error": "API key is missing"})
    #     if api_key != stored_api_key:
    #         return json.dumps({"error": "Invalid API key"})

    #     if not membership_id:
    #         return json.dumps({"error": "Membership ID is missing"})

    #     data = kw.get('data')
    #     data = data.replace("'", '"')
    #     data_dict = json.loads(data)
    #     mobile_number = data_dict.get('mobile_number') or ''
    #     membership_no = data_dict.get('membership_no') or ''
    #     member_name = data_dict.get('member_name') or ''
    #     note = data_dict.get('note') or ''
    #     portifolio_link = data_dict.get('portifolio_link') or ''
    #     portifolio_link_2 = data_dict.get('portifolio_link_2') or ''
    #     document_binary = data_dict.get('document_binary') or ''
    #     availability_from = data_dict.get('availability_from') or ''
    #     availability_till = data_dict.get('availability_till') or ''
    #     skills = data_dict.get('skills') or ''
    #     medium = data_dict.get('format_id') or ''
    #     grade = data_dict.get('grade') or ''
    #     job_seeker_id = data_dict.get('job_seeker_id') or ''
    #     skill_list = skills.split(', ')
    #     skill_ids = []
    #     for skill in skill_list:
    #         skill_id = request.env['member.skill'].sudo().search([('name', '=', skill)], limit=1)
    #         if skill_id:
    #             skill_ids.append(skill_id.id)
    #     medium_id = False
    #     if medium:
    #         medium_id = request.env['member.medium'].sudo().search([('id', '=', int(medium))], limit=1)
    #         if medium:
    #             medium_id = medium_id.id
    #     date_format = "%d/%m/%Y"
    #     if availability_from == "":
    #         availability_from = None
    #     else:
    #         availability_from = datetime.strptime(availability_from, date_format).date()
    #     if availability_till == "":
    #         availability_till = None
    #     else:
    #         availability_till = datetime.strptime(availability_till, date_format).date()
    #     if membership_id == '':
    #         return json.dumps({"error": "Membership ID is mismatched"})
    #     post_apply = data_dict.get('post_apply') or ''
    #     post_applies = False
    #     if post_apply:
    #         job_title = request.env['job.title'].sudo().search([('name', '=', post_apply)], limit=1)
    #         if job_title:
    #             post_applies = job_title.id
    #         else:
    #             job_title = request.env['job.title'].sudo().create({'name': post_apply})
    #             post_applies = job_title.id

    #     member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        
    #     job_seeker = request.env['member.job.seeker'].sudo().search([('id', '=', int(job_seeker_id))], limit=1)
    #     if job_seeker:
    #         job_seeker.sudo().write({'mobile_number': mobile_number,
    #                                  'membership_no': membership_no,
    #                                  'member_id': member.id,
    #                                  'portifolio_link': portifolio_link,
    #                                  'portifolio_link_2': portifolio_link_2,
    #                                  'member_name': member_name,
    #                                  'skill_ids': [(6, 0, skill_ids)],
    #                                  'post_applying_id': post_applies,
    #                                  'medium_id': medium_id,
    #                                  'grade': grade,
    #                                  # 'available_date': available_date.strftime("%d/%m/%Y") if available_date and isinstance(available_date, datetime.date) else None,
    #                                  'start_date': availability_from,
    #                                  'till_date': availability_till,
    #                                  'note': note,
    #                                  'document': document_binary,
    #                                  })
    #     return json.dumps({"Job Seeker Updated": job_seeker.id})


    @http.route('/post/job_seeker', type='http', auth='none', methods=['POST'], csrf=False)
    def action_post_job_seeker(self, **kw):
        api_key = kw.get('api_key')
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

        mobile_number = data_dict.get('mobile_number') or ''
        membership_no = data_dict.get('membership_no') or ''
        member_name = data_dict.get('member_name') or ''
        note = data_dict.get('note') or ''
        portifolio_link = data_dict.get('portifolio_link') or ''
        portifolio_link_2 = data_dict.get('portifolio_link_2') or ''
        document_binary = data_dict.get('document_binary') or ''
        availability_from = data_dict.get('availability_from') or ''
        availability_till = data_dict.get('availability_till') or ''
        skills = data_dict.get('skills') or ''
        medium = data_dict.get('format_id') or ''
        grade = data_dict.get('grade') or ''
        job_seeker_id = data_dict.get('job_seeker_id') or ''
        post_apply = data_dict.get('post_apply') or ''

        # Convert skills to list of ids
        skill_list = skills.split(', ')
        skill_ids = []
        for skill in skill_list:
            skill_id = request.env['member.skill'].sudo().search([('name', '=', skill)], limit=1)
            if skill_id:
                skill_ids.append(skill_id.id)

        # Get medium_id
        medium_id = False
        if medium:
            medium_rec = request.env['member.medium'].sudo().search([('id', '=', int(medium))], limit=1)
            if medium_rec:
                medium_id = medium_rec.id

        # Date parsing
        date_format = "%d/%m/%Y"
        availability_from = datetime.strptime(availability_from, date_format).date() if availability_from else None
        availability_till = datetime.strptime(availability_till, date_format).date() if availability_till else None

        # Get member
        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        if not member:
            return json.dumps({"error": "Invalid Membership ID"})

        # 🔐 Check if member's grade matches the provided grade
        if member.grade != grade:
            return json.dumps({"error": f"Grade mismatch: Member grade is '{member.grade}' but provided is '{grade}'"})

        # Get/create post_apply job title
        post_applies = False
        if post_apply:
            job_title = request.env['job.title'].sudo().search([('name', '=', post_apply)], limit=1)
            if job_title:
                post_applies = job_title.id
            else:
                job_title = request.env['job.title'].sudo().create({'name': post_apply})
                post_applies = job_title.id

        # Update job seeker
        job_seeker = request.env['member.job.seeker'].sudo().search([('id', '=', int(job_seeker_id))], limit=1)
        if job_seeker:
            job_seeker.sudo().write({
                'mobile_number': mobile_number,
                'membership_no': membership_no,
                'member_id': member.id,
                'portifolio_link': portifolio_link,
                'portifolio_link_2': portifolio_link_2,
                'member_name': member_name,
                'skill_ids': [(6, 0, skill_ids)],
                'post_applying_id': post_applies,
                'medium_id': medium_id,
                'grade': grade,
                'start_date': availability_from,
                'till_date': availability_till,
                'note': note,
                'document': document_binary,
            })
            return json.dumps({"Job Seeker Updated": job_seeker.id})
        else:
            return json.dumps({"error": "Invalid job_seeker_id"})

    @http.route('/create/job_provider', type='http', auth='none', methods=['POST'], csrf=False)
    def action_create_job_provider(self, **kw):

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
        mobile_number = data_dict.get('mobile_number') or ''
        membership_no = data_dict.get('membership_no') or ''
        member_name = data_dict.get('member_name') or ''
        note = data_dict.get('note') or ''
        required_from = data_dict.get('required_from') or ''
        required_till = data_dict.get('required_till') or ''
        skills = data_dict.get('skills') or ''
        medium = data_dict.get('format_id') or ''
        grade = data_dict.get('grade') or ''
        skill_ids = []
        if skills:
            skill_list = [s.strip() for s in skills.split(',') if s.strip()]
            for skill in skill_list:
                skill_rec = request.env['member.skill'].sudo().search([('name', '=', skill)], limit=1)
                if not skill_rec:
                    skill_rec = request.env['member.skill'].sudo().create({'name': skill})
                skill_ids.append(skill_rec.id)
        medium_ids = False
        if medium:
            medium_id = request.env['member.medium'].sudo().search([('id', '=', int(medium))], limit=1)
            if medium:
                medium_ids = medium_id.id
        date_format = "%d/%m/%Y"
        if required_from == "":
            required_from = None
        else:
            required_from = datetime.strptime(required_from, date_format).date()
        if required_till == "":
            required_till = None
        else:
            required_till = datetime.strptime(required_till, date_format).date()
        if membership_id == '':
            return json.dumps({"error": "Membership ID is mismatched"})
        post_required = data_dict.get('post_required') or ''
        post_requireds = False
        if post_required:
            job_title = request.env['job.title'].sudo().search([('name', '=', post_required)], limit=1)
            if job_title:
                post_requireds = job_title.id
            else:
                job_title = request.env['job.title'].sudo().create({'name': post_required})
                post_requireds = job_title.id

        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        job_provider = request.env['member.job.provider'].sudo().create({'mobile_number': mobile_number,
                                                                         'membership_no': membership_no,
                                                                         'member_id': member.id,
                                                                         'member_name': member_name,
                                                                         'skill_ids': [(6, 0, skill_ids)],
                                                                         'post_required_id': post_requireds,
                                                                         'medium_id': medium_ids,
                                                                         'grade': grade,
                                                                         # 'available_date': available_date.strftime("%d/%m/%Y") if available_date and isinstance(available_date, datetime.date) else None,
                                                                         'required_from': required_from,
                                                                         'required_till': required_till,
                                                                         'note': note,

                                                                         })
        job_provider.send_push_to_job_seekers()
        return json.dumps({'membership': 'Job Provider Created', 'ID': job_provider.id})

    @http.route('/get/member/job_provider', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_member_job_provider(self, **kw):

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
        if member:
            job_provider_vals = []
            job_provider_ids = request.env['member.job.provider'].sudo().search([('member_id', '=', member.id)])
            for job_provider in job_provider_ids:
                vals = {
                    'membership_no': job_provider.membership_no or '',
                    'member_id': member.id or False,
                    'member_name': job_provider.member_name or '',
                    'skill_ids': [{'id': skill.id, 'name': skill.name} for skill in
                                  job_provider.skill_ids],
                    'post_required_id': job_provider.post_required_id.name or '',
                    'format_name': job_provider.medium_id.name or '',
                    'format_id': job_provider.medium_id.id or '',
                    'grade': job_provider.grade or '',
                    # 'available_date': available_date.strftime("%d/%m/%Y") if available_date and isinstance(available_date, datetime.date) else None,
                    'required_from': job_provider.required_from.strftime(
                        "%Y-%m-%d") if job_provider.required_from else '',
                    'required_till': job_provider.required_till.strftime(
                        "%Y-%m-%d") if job_provider.required_till else '',
                    'note': job_provider.note,
                    'job_provider_id': job_provider.id
                }
                job_provider_vals.append(vals)
            return json.dumps({'Member Job Seeker': job_provider_vals})

    @http.route('/post/job_provider', type='http', auth='none', methods=['POST'], csrf=False)
    def action_post_job_provider(self, **kw):

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
        mobile_number = data_dict.get('mobile_number') or ''
        membership_no = data_dict.get('membership_no') or ''
        member_name = data_dict.get('member_name') or ''
        note = data_dict.get('note') or ''
        required_from = data_dict.get('required_from') or ''
        required_till = data_dict.get('required_till') or ''
        skills = data_dict.get('skills') or ''
        medium = data_dict.get('format_id') or ''
        grade = data_dict.get('grade') or ''
        job_provider_id = data_dict.get('job_provider_id') or ''
        skill_list = skills.split(', ')
        skill_ids = []
        for skill in skill_list:
            skill_id = request.env['member.skill'].sudo().search([('name', '=', skill)], limit=1)
            if skill_id:
                skill_ids.append(skill_id.id)
        medium_id = False
        if medium:
            medium_id = request.env['member.medium'].sudo().search([('id', '=', int(medium))], limit=1)
            if medium:
                medium_id = medium_id.id
        date_format = "%d/%m/%Y"
        if required_from == "":
            required_from = None
        else:
            required_from = datetime.strptime(required_from, date_format).date()
        if required_till == "":
            required_till = None
        else:
            required_till = datetime.strptime(required_till, date_format).date()
        if membership_id == '':
            return json.dumps({"error": "Membership ID is mismatched"})
        post_required = data_dict.get('post_required') or ''
        post_requireds = False
        if post_required:
            job_title = request.env['job.title'].sudo().search([('name', '=', post_required)], limit=1)
            if job_title:
                post_requireds = job_title.id
            else:
                job_title = request.env['job.title'].sudo().create({'name': post_required})
                post_requireds = job_title.id

        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        job_provider_id = request.env['member.job.provider'].sudo().search([('id', '=', int(job_provider_id))], limit=1)
        if job_provider_id:
            job_provider_id.sudo().write({'mobile_number': mobile_number,
                                          'membership_no': membership_no,
                                          'member_id': member.id,
                                          'member_name': member_name,
                                          'skill_ids': [(6, 0, skill_ids)],
                                          'post_required_id': post_requireds,
                                          'medium_id': medium_id,
                                          'grade': grade,
                                          # 'available_date': available_date.strftime("%d/%m/%Y") if available_date and isinstance(available_date, datetime.date) else None,
                                          'required_from': required_from,
                                          'required_till': required_till,
                                          'note': note,

                                          })
            return json.dumps({'Job Provider Updated': job_provider_id.id})

    @http.route('/all/job_provider', type='http', auth='none', methods=['GET'], csrf=False)
    def action_all_job_provider(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')  # Corrected case for 'membership_id'
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        member_job_provider_ids = request.env['member.job.provider'].sudo().search([])
        designation_ids = member_job_provider_ids.mapped('designation')
        all_job_provider_details = []
        for designation in designation_ids:
            job_designation = request.env['member.job.provider'].sudo().search([('designation', '=', designation)])
            job_provider = []
            for design in job_designation:
                vals = {
                    'mobile_number': design.mobile_number,
                    'membership_no': design.membership_no,
                    'member_id': design.member_id.id,
                    'skill': design.skill,
                    'experience': design.experience,
                    'portifolio_link': design.portifolio_link,
                    'designation': design.designation,
                    'member_name': design.member_name,
                    # 'project_requirement': design.project_requirement,
                    # 'medium': [(6,0, design.medium.ids)],
                    'project_requirement': [{'id': project.id, 'name': project.name} for project in
                                            design.project_requirement],
                    'medium': [{'id': med.id, 'name': med.name} for med in design.medium],
                    'note': design.note,
                    'job_provide_id': design.id
                }
                job_provider.append(vals)
            all_job_provider_details.append({'designation': designation, 'jobs_provider': vals})
        return json.dumps({'job_provider_details': all_job_provider_details})

    @http.route('/get/job_provider', type='http', auth='none', methods=['GET'], csrf=False)
    def get_job_provider_by_member_id(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')  # Corrected case for 'membership_id'
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        job_provider_list = []
        for job_provider in request.env['member.job.provider'].sudo().search([('membership_no', '=', membership_id)]):
            vals = {}
            vals['mobile_number'] = job_provider.mobile_number
            vals['membership_no'] = job_provider.membership_no
            vals['member_id'] = job_provider.member_id.id
            vals['skill'] = job_provider.skill
            vals['experience'] = job_provider.experience
            vals['portifolio_link'] = job_provider.portifolio_link
            vals['designation'] = job_provider.designation
            vals['member_name'] = job_provider.member_name
            vals['project_requirement'] = job_provider.project_requirement[
                0].name if job_provider.project_requirement else ''
            # vals['project_requirement'] = [{'id': project.id, 'name': project.name} for project in job_provider.project_requirement]
            # vals['project_requirement_ids'] = job_provider.project_requirement.ids
            vals['medium'] = job_provider.medium[0].name if job_provider.medium else ''
            # vals['medium'] = [{'id': med.id, 'name': med.name} for med in job_provider.medium]
            # vals['medium_ids'] = job_provider.medium.ids
            vals['note'] = job_provider.note
            vals['job_provide_id'] = job_provider.id
            job_provider_list.append(vals)
        return json.dumps({'job_provider_details': job_provider_list})

    @http.route('/get/all/match_job_seeker', type='http', auth='none', methods=['GET'], csrf=False)
    def get_all_matched_job_seeker(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        membership_no = kw.get('MEMBERSHIP_ID')  # Extract the API key from the GET parameters
        job_provide_id = kw.get('job_provide_id')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        job_details = []
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        today = fields.Date.today()
        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_no)], limit=1)
        filter_job_provider = request.env['member.job.provider'].sudo().search([('required_till', '>', today), ('member_id', '=', member.id), ('id', '=', int(job_provide_id))], limit=1)
        for job_provide in filter_job_provider:
            job_seeker_ids = []

            filter_by_date = request.env['member.job.seeker'].sudo().search(
                [('till_date', '<=', job_provide.required_till), ('start_date', '>=', job_provide.required_from)])
            count = 1
            job_seeker_details = []
            for job_seeker in filter_by_date:
                percentage = 25
                if any(skill.id in job_provide.skill_ids.ids for skill in job_seeker.skill_ids):
                    percentage += 25
                    count += 1
                if job_seeker.medium_id.id == job_provide.medium_id.id :
                    percentage += 25
                    count += 1
                if job_seeker.post_applying_id.id == job_provide.post_required_id.id :
                    percentage += 25
                    count += 1
                if count > 0:
                    job_seeker_ids.append(job_seeker.id)
                job_seeker_vals = {
                    'membership_no': job_seeker.membership_no or '',
                    'member_id': member.id or False,
                    'contact1': member.contact1 or '',
                    'contact2': member.contact2 or '',
                    'email': member.email or '',
                    'document_binary': job_seeker.document or '',
                    'portifolio_link': job_seeker.portifolio_link or '',
                    'portifolio_link_2': job_seeker.portifolio_link_2 or '',
                    'member_name': job_seeker.member_name or '',
                    'skill_ids': [{'id': skill.id, 'name': skill.name} for skill in
                                  job_seeker.skill_ids],
                    'post_applying_id': job_seeker.post_applying_id.name or '',
                    'medium_id': job_seeker.medium_id.name or '',
                    'grade': job_seeker.grade or '',
                    # 'available_date': available_date.strftime("%d/%m/%Y") if available_date and isinstance(available_date, datetime.date) else None,
                    'start_date': job_seeker.start_date.strftime("%Y-%m-%d") if job_seeker.start_date else '',
                    'till_date': job_seeker.till_date.strftime("%Y-%m-%d") if job_seeker.till_date else '',
                    'note': job_seeker.note,
                    'job_seeker_id': job_seeker.id,
                    'percentage': percentage or 0,
                }
                job_seeker_details.append(job_seeker_vals)

            job_provide_vals = {
                'membership_no': job_provide.membership_no or '',
                    'member_id': member.id or False,
                    'member_name': job_provide.member_name or '',
                    'skill_ids': [{'id': skill.id, 'name': skill.name} for skill in
                                  job_provide.skill_ids],
                    'post_required_id': job_provide.post_required_id.name or '',
                    'medium_id': job_provide.medium_id.name or '',
                    'grade': job_provide.grade or '',
                    # 'available_date': available_date.strftime("%d/%m/%Y") if available_date and isinstance(available_date, datetime.date) else None,
                    'required_from': job_provide.required_from.strftime(
                        "%Y-%m-%d") if job_provide.required_from else '',
                    'required_till': job_provide.required_till.strftime(
                        "%Y-%m-%d") if job_provide.required_till else '',
                    'note': job_provide.note,
                    'job_provider_id': job_provide.id
            }
            job_details.append({'job_provider': job_provide_vals, 'job seeker': job_seeker_details})

        return json.dumps({"job details": job_details})

    @http.route('/get/match_job_seeker', type='http', auth='none', methods=['GET'], csrf=False)
    def get_matched_job_seeker(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters goutham
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        job_seeker_details = []
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})

        till_date = kw.get('till_date')
        project_requirement_ids = kw.get('project_requirement_ids')
        medium_ids = kw.get('medium_ids')

        # print("\n\n\n", till_date,"\n", project_requirement_ids,"\n", medium_ids,"\n\n\n")

        if not all([till_date, project_requirement_ids, medium_ids]):
            return json.dumps({"error": "Invalid Param : till_date, project_requirement_ids, medium_ids"})

        job_seekers = request.env['member.job.seeker'].sudo().search(
            [('till_date', '<=', till_date), ('post_applying_ids_json', '=', project_requirement_ids),
             ('medium_ids_json', '=', medium_ids)])
        if not job_seekers:
            job_seekers = request.env['member.job.seeker'].sudo().search(
                [('till_date', '<=', till_date), ('post_applying_ids_json', '=', project_requirement_ids)])
            job_seekers += request.env['member.job.seeker'].sudo().search(
                [('till_date', '<=', till_date),
                 ('medium_ids_json', '=', medium_ids)]
            )

        for job_seeker in job_seekers:
            job_seeker_details.append({
                'mobile_number': job_seeker.mobile_number,
                'membership_no': job_seeker.membership_no,
                'member_id': job_seeker.member_id.id,
                'skill_1': job_seeker.skill_1,
                'skill_2': job_seeker.skill_2,
                'experience': job_seeker.experience,
                # 'date': job_seeker.available_date,
                'till_date': job_seeker.till_date.strftime(
                    "%Y-%m-%d") if job_seeker.till_date else '',
                'start_date': job_seeker.start_date.strftime(
                    "%Y-%m-%d") if job_seeker.start_date else '',
                'portifolio_link': job_seeker.portifolio_link,
                'designation': job_seeker.designation,
                'member_name': job_seeker.member_name,
                # 'project_requirement': job_seeker.post_applying,
                # 'medium': job_seeker.medium,
                'project_requirement': [{'id': post.id, 'name': post.name} for post in
                                        job_seeker.post_applying],
                'medium': [{'id': med.id, 'name': med.name} for med in job_seeker.medium],
                'note': job_seeker.note
            })
        return json.dumps({"job_seekers": job_seeker_details})

    @http.route('/get/all/member/match_job_seeker', type='http', auth='none', methods=['GET'], csrf=False)
    def get_all_member_matched_job_seeker(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        job_details = []
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        membership_id = kw.get('MEMBERSHIP_ID')
        job_provide_id = kw.get('job_provide_id')
        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        today = fields.Date.today()
        filter_job_provider = request.env['member.job.provider'].sudo().search(
            [('required_till', '>', today), ('member_id', '=', member.id), ('id', '=', int(job_provide_id))], limit=1)
        for job_provide in filter_job_provider:
            job_seeker_ids = []

            filter_by_date = request.env['member.job.seeker'].sudo().search(
                [('till_date', '<=', job_provide.required_till)])

            for job_seeker in filter_by_date:
                if any(med.id in job_provide.medium.ids for med in job_seeker.medium):
                    if job_seeker.id not in job_seeker_ids:
                        job_seeker_ids.append(job_seeker.id)
            for job_seeker in filter_by_date:
                if any(post.id in job_provide.project_requirement.ids for post in job_seeker.post_applying):
                    if job_seeker.id not in job_seeker_ids:
                        job_seeker_ids.append(job_seeker.id)

            job_seeker_details = []
            job_provide_vals = {
                'mobile_number': job_provide.mobile_number,
                'job_provide_reference': job_provide.name,
                'membership_no': job_provide.membership_no,
                'member_id': job_provide.member_id.id,
                'skill': job_provide.skill,
                'experience': job_provide.experience,
                'portifolio_link': job_provide.portifolio_link,
                'designation': job_provide.designation,
                'member_name': job_provide.member_name,
                # 'project_requirement': job_provide.project_requirement,
                # 'medium': job_provide.medium,
                'project_requirement': [{'id': project.id, 'name': project.name} for project in
                                        job_provide.project_requirement],
                'medium': [{'id': med.id, 'name': med.name} for med in job_provide.medium],
                'date': job_provide.date.strftime("%Y-%m-%d") if job_provide.date else '',
                'note': job_provide.note,
                'job_provide_id': job_provide.id
            }
            for job_seeker in job_seeker_ids:
                job_seeker = request.env['member.job.seeker'].sudo().search([('id', '=', job_seeker)], limit=1)
                job_seeker_vals = {
                    'mobile_number': job_seeker.mobile_number,
                    'membership_no': job_seeker.membership_no,
                    'member_id': job_seeker.member_id.id,
                    'skill_1': job_seeker.skill_1,
                    'skill_2': job_seeker.skill_2,
                    'experience': job_seeker.experience,
                    # 'date': job_seeker.available_date,
                    # 'available_date': job_seeker.available_date.strftime(
                    #     "%Y-%m-%d") if job_seeker.available_date else '',
                    'start_date': job_seeker.start_date.strftime(
                        "%Y-%m-%d") if job_seeker.start_date else '',
                    'till_date': job_seeker.till_date.strftime(
                        "%Y-%m-%d") if job_seeker.till_date else '',
                    'portifolio_link': job_seeker.portifolio_link,
                    'designation': job_seeker.designation,
                    'member_name': job_seeker.member_name,
                    # 'project_requirement': job_seeker.post_applying,
                    # 'medium': job_seeker.medium,
                    'project_requirement': [{'id': post.id, 'name': post.name} for post in
                                            job_seeker.post_applying],
                    'medium': [{'id': med.id, 'name': med.name} for med in job_seeker.medium],
                    'note': job_seeker.note,
                    'document': job_seeker.document
                }
                job_seeker_details.append(job_seeker_vals)

            job_details.append({'job_provider': job_provide_vals, 'job seeker': job_seeker_details})

        return json.dumps({"job details": job_details})

    @http.route('/api/member_job_seeker_list', type='json', auth='none', methods=['POST'], csrf=False)
    def member_job_seeker_list(self, **kw):
        try:
            # Try to get payload from kw (type='json' normally populates kw)
            payload = kw or {}
            raw_body = None

            # If kw is empty, try to read raw request body and parse JSON
            if not payload:
                try:
                    raw_body = request.httprequest.data.decode('utf-8') or ''
                    if raw_body:
                        payload = json.loads(raw_body)
                except Exception as e:
                    _logger.debug("Could not parse raw body: %s", e)
                    payload = {}

            # API key validation
            api_key = payload.get('api_key') if isinstance(payload, dict) else None
            stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
            if api_key != stored_api_key:
                return {"status": 403, "message": "Invalid API Key", "received": payload}

            JobSeeker = request.env['member.job.seeker'].sudo()
            seekers = JobSeeker.search([])

            result = []
            for rec in seekers:
                # safe conversion helpers
                def ds(d): return fields.Date.to_string(d) if d else False
                # Binary fields are already base64-encoded in Odoo; ensure str or False
                doc_bin = False
                pic_bin = False
                try:
                    if rec.document_binary:
                        # ensure bytes -> str
                        if isinstance(rec.document_binary, bytes):
                            doc_bin = base64.b64encode(rec.document_binary).decode('utf-8')
                        else:
                            # often it's already a base64 string
                            doc_bin = rec.document_binary.decode('utf-8') if isinstance(rec.document_binary, memoryview) else str(rec.document_binary)
                    if rec.profile_pic:
                        if isinstance(rec.profile_pic, bytes):
                            pic_bin = base64.b64encode(rec.profile_pic).decode('utf-8')
                        else:
                            pic_bin = rec.profile_pic.decode('utf-8') if isinstance(rec.profile_pic, memoryview) else str(rec.profile_pic)
                except Exception:
                    # fallback: just mark presence
                    doc_bin = None if not rec.document_binary else True
                    pic_bin = None if not rec.profile_pic else True

                result.append({
                    "id": rec.id,
                    "name": rec.name,
                    "member_id": rec.member_id.id if rec.member_id else False,
                    "member_name": rec.member_name or (rec.member_id and rec.member_id.name) or False,
                    "mobile_number": rec.mobile_number or False,
                    "membership_no": rec.membership_no or False,
                    "designation": rec.designation or False,
                    "grade": rec.grade or False,
                    "skill_1": rec.skill_1 or False,
                    "skill_2": rec.skill_2 or False,
                    "skill_ids": rec.skill_ids.ids,
                    "skill_names": rec.skill_ids.mapped('name'),
                    "post_applying": rec.post_applying.ids,            # many2many of job.title
                    "post_applying_names": rec.post_applying.mapped('name'),
                    "post_applying_id": rec.post_applying_id.id if rec.post_applying_id else False,
                    "post_applying_id_name": rec.post_applying_id.name if rec.post_applying_id else False,
                    "post_applying_ids_json": rec.post_applying_ids_json or False,
                    "start_date": ds(rec.start_date),
                    "till_date": ds(rec.till_date),
                    "available_date": ds(rec.available_date),
                    "experience": rec.experience or False,
                    "portifolio_link": rec.portifolio_link or False,
                    "portifolio_link_2": rec.portifolio_link_2 or False,
                    "note": rec.note or False,
                    "document": rec.document or False,
                    "document_binary_base64": doc_bin,   # WARNING: can be large
                    "has_document_binary": bool(rec.document_binary),
                    "profile_pic_base64": pic_bin,       # WARNING: can be large
                    "has_profile_pic": bool(rec.profile_pic),
                    "medium_ids": rec.medium.ids,
                    "medium_names": rec.medium.mapped('name'),
                    "medium_id": rec.medium_id.id if rec.medium_id else False,
                    "medium_id_name": rec.medium_id.name if rec.medium_id else False,
                    "state": rec.state,
                    "active": bool(rec.active),
                })

            return {"status": 200, "count": len(result), "data": result}

        except Exception as e:
            _logger.exception("Error in member_job_seeker_list")
            return {
                "status": 500,
                "message": "An error occurred while fetching member job seeker list",
                "error": str(e),
                "debug_received_kw": kw
            }
