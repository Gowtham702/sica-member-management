import binascii

from odoo import http, fields
from odoo.http import request
import json
import base64
import io
from PIL import Image
from datetime import datetime


class SicaSupport(http.Controller):

    @http.route('/sica/support/json', type="json", auth='none', methods=['POST'], csrf=False)
    def action_create_support_tickets_json(self, **kw):
        payload = request.httprequest.data.decode()
        payload = json.loads(payload)

        api_key = payload.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = payload.get('MEMBERSHIP_ID')
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})

        member_name = payload.get('member_name')
        image = payload.get('image')
        date = payload.get('date')
        if date:
            date_obj = datetime.strptime(date, '%d-%m-%Y')  # Convert to datetime
            formatted_date = date_obj.strftime('%Y-%m-%d')
        else:
            formatted_date = False
        type_of_issue = payload.get('type_of_issue')
        details = payload.get('details')
        app_version = payload.get('app_version')
        additional_notes = payload.get('additional_notes')

        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        if member:
            support_ticket = request.env['sica.support'].sudo().create({
                'member_id': member.id,
                'member_name': member_name,
                'image_1920': image,
                'date': formatted_date,
                'type_of_issue': type_of_issue,
                'details': details,
                'app_version': app_version,
                'additional_notes': additional_notes
            })
            return json.dumps({'Sica Support Ticket ID ': support_ticket.support_no})
        else:
            return json.dumps({"error": "Membership ID is mismatched"})