from odoo import http, fields
from odoo.http import request
import json
import random
import requests
import datetime
from datetime import datetime
import razorpay

class Grievance(http.Controller):
    @http.route('/get/all/grievance_reason', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_grievance_reason(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        grievance_ids = request.env['grievance.reason'].sudo().search([])
        reason_details = []
        for grievance in grievance_ids:
            reason_details.append({
                'reason_name': grievance.name,
                'reason_id': grievance.id,
                'is_production_update': grievance.is_production_update
            })
        return json.dumps({'grievance_reason_details': reason_details})

    @http.route('/create/grievance_report', type='http', auth='none', methods=['POST'], csrf=False)
    def action_create_job_provider(self, **kw):

        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')  # Corrected case for 'membership_id'
        reason_id = kw.get('Reason_id')  # Corrected case for 'membership_id'

        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})

        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        data = kw.get('data')
        data = data.replace("'", '"')
        data_dict = json.loads(data)
        member_name_no = data_dict.get('member_name_no') or ''
        name = data_dict.get('name') or ''
        project_name = data_dict.get('project_name') or ''
        projection_house_name = data_dict.get('projection_house_name') or ''
        outdoor_unit_name = data_dict.get('outdoor_unit_name') or ''
        location = data_dict.get('location') or ''
        issue_raised = data_dict.get('issue_raised') or ''
        issue_type = data_dict.get('issue_type') or ''
        approximate_time_lost = data_dict.get('approximate_time_lost') or ''
        contact_outdoor_unit_manager = data_dict.get('contact_outdoor_unit_manager') or ''
        has_outdoor_unit_manager_helpful_to_the_solve_issue = data_dict.get(
            'has_outdoor_unit_manager_helpful_to_the_solve_issue') or ''
        name_contact_no_of_production_manager_executive_producer = data_dict.get(
            'name_contact_no_of_production_manager_executive_producer') or ''
        brief_issue_faced_with_service_of_outdoor_unit_equipment = data_dict.get(
            'brief_issue_faced_with_service_of_outdoor_unit_equipment') or ''
        issue_has_been_reported = data_dict.get('issue_has_been_reported') or ''

        if membership_id == '':
            return json.dumps({"error": "Membership ID is mismatched"})
        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        grievance_report = request.env['grievance.report'].sudo().create({
            'member_name_no': member_name_no,
            'member_id': member.id,
            'grievance_reason_id': reason_id,
            'name': name,
            'project_name': project_name,
            'projection_house_name': projection_house_name,
            'outdoor_unit_name': outdoor_unit_name,
            'location': location,
            'contact_outdoor_unit_manager': contact_outdoor_unit_manager,
            'approximate_time_lost': approximate_time_lost,
            'has_outdoor_unit_manager_helpful_to_the_solve_issue': has_outdoor_unit_manager_helpful_to_the_solve_issue,
            'name_contact_no_of_production_manager_executive_producer': name_contact_no_of_production_manager_executive_producer,
            'brief_issue_faced_with_service_of_outdoor_unit_equipment': brief_issue_faced_with_service_of_outdoor_unit_equipment,
            'issue_has_been_reported': issue_has_been_reported,
            'issue_type': issue_type,
        })
        return json.dumps({'membership': 'Grievance Report Created', 'ID': grievance_report.id})

class DailyShootingUpdate(http.Controller):
    @http.route('/create/daily_shooting_update', type='http', auth='none', methods=['POST'], csrf=False)
    def action_create_job_provider(self, **kw):

        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')  # Corrected case for 'membership_id'
        reason_id = kw.get('Reason_id')  # Corrected case for 'membership_id'

        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})

        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        data = kw.get('data')
        data = data.replace("'", '"')
        data_dict = json.loads(data)
        member_name = data_dict.get('member_name') or ''
        email = data_dict.get('email') or ''
        date = data_dict.get('date') or ''
        member_contact_no = data_dict.get('member_contact_no') or ''
        membership_no = data_dict.get('membership_no') or ''
        category = data_dict.get('category') or ''
        project_title = data_dict.get('project_title') or ''
        format = data_dict.get('format') or ''
        designation = data_dict.get('designation') or ''
        producer = data_dict.get('producer') or ''
        project_house = data_dict.get('project_house') or ''
        production_executive = data_dict.get('production_executive') or ''
        production_executive_contact_no = data_dict.get('production_executive_contact_no') or ''
        outdoor_unit_name = data_dict.get('outdoor_unit_name') or ''
        location = data_dict.get('location') or ''
        date_format = "%d/%m/%Y"
        if date == "":
            date = None
        else:
            date = datetime.strptime(date, date_format).date()

        if membership_id == '':
            return json.dumps({"error": "Membership ID is mismatched"})
        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        daily_shooting_update = request.env['daily.shooting.update'].sudo().create({
            'date': date,
            'member_id': member.id,
            'grievance_reason_id': reason_id,
            'member_contact_no': member_contact_no,
            'member_name': member_name,
            'email': email,
            'membership_no': membership_no,
            'category': category,
            'project_title': project_title,
            'format': format,
            'designation': designation,
            'producer': producer,
            'project_house': project_house,
            'production_executive': production_executive,
            'production_executive_contact_no': production_executive_contact_no,
            'outdoor_unit_name':outdoor_unit_name,
            'location': location,

        })
        return json.dumps({'Daily Shooting Update': 'Created', 'ID': daily_shooting_update.reference})
