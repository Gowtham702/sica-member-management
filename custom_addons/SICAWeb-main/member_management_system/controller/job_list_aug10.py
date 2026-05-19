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

class JobList(http.Controller):

    @http.route('/api/job_list/', type='json', auth='none', methods=['POST'], csrf=False)
    def active_job_list(self, **kw):
        try:
            api_key = kw.get('api_key')
            print(11111111111111111111111111111111111111111111111)
            print(api_key)
            stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"

            if api_key != stored_api_key:
                return {
                    "status": 403,
                    "message": "Invalid API Key"
                }

            records = request.env['member.job.provider'].sudo().search([('state', '=', 'active')])
            result = []
            for rec in records:
                result.append({
                    "id": rec.id,
                    "member_name": rec.member_name,
                    "mobile_number": rec.mobile_number,
                    "designation": rec.designation,
                    "experience": rec.experience,
                    "skills": [skill.name for skill in rec.skill_ids],
                    "project_requirements": [proj.name for proj in rec.project_requirement],
                    "available_start_date": rec.available_start_date.strftime('%Y-%m-%d') if rec.available_start_date else None,
                    "available_end_date": rec.available_end_date.strftime('%Y-%m-%d') if rec.available_end_date else None,
                    "state": rec.state,
                })

            return {
                "status": 200,
                "data": result
            }

        except Exception as e:
            return {
                "status": 500,
                "message": "An error occurred while fetching job list",
                "error": str(e)
            }
        
    @http.route('/api/description/', type='json', auth='none', methods=['POST'], csrf=False)
    def active_description(self, **kw):
        try:
            api_key = kw.get('api_key')
            record_id = kw.get('id')  # Avoid using 'id' as variable name

            stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"

            if api_key != stored_api_key:
                return {
                    "status": 403,
                    "message": "Invalid API Key"
                }

            if not record_id:
                return {
                    "status": 400,
                    "message": "Missing required parameter: id"
                }

            # Make sure it's an integer
            try:
                record_id = int(record_id)
            except ValueError:
                return {
                    "status": 400,
                    "message": "Invalid ID format"
                }

            # Proper domain structure
            records = request.env['member.job.provider'].sudo().search([
                ('state', '=', 'active'),
                ('id', '=', record_id)
            ])

            result = []
            for rec in records:
                result.append({
                    "id": rec.id,
                    "description": rec.note,
                    "mobile_number": rec.mobile_number,
                    "designation": rec.designation,
                    "experience": rec.experience,
                    "skills": [skill.name for skill in rec.skill_ids],
                    "project_requirements": [proj.name for proj in rec.project_requirement],
                    "available_start_date": rec.available_start_date.strftime('%Y-%m-%d') if rec.available_start_date else None,
                    "available_end_date": rec.available_end_date.strftime('%Y-%m-%d') if rec.available_end_date else None,
                    "state": rec.state,
                })

            return {
                "status": 200,
                "data": result
            }

        except Exception as e:
            return {
                "status": 500,
                "message": "An error occurred while fetching job description",
                "error": str(e)
            }
        
    
    @http.route('/api/job/history/', type='json', auth='none', methods=['POST'], csrf=False)
    def applyed_job(self, **kw):
        # try:
            member_id = kw.get("id")
            print("https://app.thesica.in/: ", member_id)
            if not member_id:
                return {
                    "status": 400,
                    "message": "Missing 'id' parameter for member_id"
                }
            _logger.error("Error in /api/job/history/ for member_id %s: %s", member_id)
            # Fetch job seeker records for the given member
            job_applications = request.env['member.job.seeker'].sudo().search([('member_id', '=', int(member_id))])
            # app = request.env['member.job.seeker'].sudo().search([])
            # print(app.member_id.id)
            _logger.error("Error in /api/job/history/2 for job_applications %s: %s", job_applications)

            result = []
            for record in job_applications:
                jobs = record.post_applying.mapped('name')  # Assuming 'name' field in job.title model
                result.append({
                    "job_seeker_id": record.id,
                    "member_id": record.member_id.id,
                    "member_name": record.member_id.name,
                    "applied_jobs": jobs
                })

            return {
                "status": 200,
                "message": "Job application history retrieved successfully",
                "data": result
            }

        # except Exception as e:
        #     _logger.error("Error in /api/job/history/ for member_id %s: %s", kw.get("id"), str(e))
        #     return {
        #         "status": 500,
        #         "message": "An error occurred while fetching job history",
        #         "error": str(e)
        #     }