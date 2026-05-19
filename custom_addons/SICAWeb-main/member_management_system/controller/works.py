from odoo import http, fields
from odoo.http import request
import json
import random
import requests
import datetime
from datetime import datetime
import razorpay

class MemberWorks(http.Controller):

    @http.route('/create/work_details/json', type="json", auth='none', methods=['POST'], csrf=False)
    def action_create_work_details_json(self, args=None, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        payload = request.httprequest.data.decode()
        payload = json.loads(payload)
        msg = []
        success = {'code': 200, 'status': 'Success'}

        api_key = payload.get('api_key')
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"

        membership_id = payload.get('MEMBERSHIP_ID')
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})

        project_name = payload.get('project_name')
        year = payload.get('year')
        designation = payload.get('designation')
        format = payload.get('format')
        dop_name = payload.get('dop_name')
        image = payload.get('image')
        proof_image = payload.get('proof_image')
        weblink = payload.get('weblink')
        language = payload.get('language')

        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        if member:
            create_works = request.env['member.work'].sudo().create({
                'project_name': project_name,
                'year': year,
                'request_type': 'Create',
                'designation': designation,
                'approve_status': 'Waiting_for_approval',
                'duplicate_member_id': member.id,
                'member_id': member.id,
                'format': format,
                'dop_name': dop_name,
                'image': image,
                'proof_image': proof_image,
                'weblink': weblink,
                'language': language,
            })
            return json.dumps({'works': 'request works created - waiting for the approval', 'ID': create_works.id})
        else:
            return json.dumps({"error": "Membership ID is mismatched"})

    @http.route('/update/work_details/json', type='json', auth='none', methods=['POST'], csrf=False)
    def action_update_work_details_json(self, **kw):
        payload = request.httprequest.data.decode()
        payload = json.loads(payload)
        id = payload.get('ID')
        api_key = payload.get('api_key')
        membership_id = payload.get('MEMBERSHIP_ID')
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"

        # id = kw.get('ID')
        # api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        # stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        # membership_id = kw.get('MEMBERSHIP_ID')
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        project_name = payload.get('project_name')
        year = payload.get('year')
        designation = payload.get('designation')
        format = payload.get('format')
        dop_name = payload.get('dop_name')
        image = payload.get('image')
        proof_image = payload.get('proof_image')
        weblink = payload.get('weblink')
        language = payload.get('language')


        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        if member:
            work = request.env['member.work'].sudo().search(
                [('member_id', '=', member.id), ('id', '=', int(id))], limit=1)
            if work:
                create_works = request.env['member.work'].sudo().create({
                    'project_name': project_name,
                    'year': year,
                    'request_type': 'Update',
                    'designation': designation,
                    'duplicate_member_id': member.id,
                    'approve_status': 'Waiting_for_approval',
                    'work_id': work.id,
                    'format': format,
                    'dop_name': dop_name,
                    'image': image,
                    'proof_image': proof_image,
                    'weblink': weblink,
                    'language': language,
                })
                return json.dumps({'works': ' request works update - waiting for the approval', 'ID': work.id})
            else:
                return json.dumps({'error': 'Id is not Mismatched'})
        else:
            return json.dumps({"error": "Membership ID is mismatched"})



    @http.route('/create/work_details', type='http', auth='none', methods=['POST'], csrf=False)
    def action_create_work_details(self, **kw):
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
        project_name = data_dict.get('project_name')
        year = data_dict.get('year')
        designation = data_dict.get('designation')
        format = data_dict.get('format')
        dop_name = data_dict.get('dop_name')
        image = data_dict.get('image')

        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        if member:
            create_works = request.env['member.work'].sudo().create({
                'project_name': project_name,
                'year': year,
                'request_type': 'Create',
                'designation': designation,
                'approve_status': 'Waiting_for_approval',
                'duplicate_member_id': member.id,
                'format': format,
                'dop_name': dop_name,
                'image': image,
            })
            return json.dumps({'works': 'request works created - waiting for the approval', 'ID': create_works.id})
        else:
            return json.dumps({"error": "Membership ID is mismatched"})

    @http.route('/update/work_details', type='http', auth='none', methods=['POST'], csrf=False)
    def action_update_work_details(self, **kw):
        id = kw.get('ID')
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
        project_name = data_dict.get('project_name')
        year = data_dict.get('year')
        designation = data_dict.get('designation')
        format = data_dict.get('format')
        dop_name = data_dict.get('dop_name')
        image = data_dict.get('image')

        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        if member:
            work = request.env['member.work'].sudo().search(
                [('member_id', '=', member.id), ('id', '=', id)], limit=1)
            if work:
                create_works = request.env['member.work'].sudo().create({
                    'project_name': project_name,
                    'year': year,
                    'request_type': 'Update',
                    'designation': designation,
                    'duplicate_member_id': member.id,
                    'approve_status': 'Waiting_for_approval',
                    'work_id': work.id,
                    'format': format,
                    'dop_name': dop_name,
                    'image': image
                })
                return json.dumps({'works': ' request works update - waiting for the approval', 'ID': work.id})
            else:
                return json.dumps({'error': 'Id is not Mismatched'})
        else:
            return json.dumps({"error": "Membership ID is mismatched"})

    @http.route('/delete/work_details', type='http', auth='none', methods=['DELETE'], csrf=False)
    def action_delete_work_details(self, **kw):
        api_key = kw.get('api_key')
        id = kw.get('ID')  # Extract the API key from the GET parameters
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
            work = request.env['member.work'].sudo().search(
                [('member_id', '=', member.id), ('id', '=', id)], limit=1)
            if work:
                work.write({
                    'request_type': 'Delete',
                    'approve_status': 'Waiting_for_approval',
                    'duplicate_member_id': member.id
                })
                return json.dumps({'works': 'request works deleted- waiting for the approval'})
            else:
                return json.dumps({'error': "Record not found"})

        else:
            return json.dumps({"error": "Membership ID is mismatched"})
