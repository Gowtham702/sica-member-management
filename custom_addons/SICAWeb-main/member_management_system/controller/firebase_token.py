import binascii

from odoo import http, fields
from odoo.http import request
import json
import base64
import logging
import io
from PIL import Image
from datetime import datetime

_logger = logging.getLogger(__name__)  # <-- THIS IS THE MISSING LINE

class SicaSupport(http.Controller):

    @http.route('/firebase/token/json', type="json", auth='none', methods=['POST'], csrf=False)
    def action_create_firebase_token_json(self, **kw):
        print("111111111111111111111111111111111111111111111")
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

        token = payload.get('token')
        if not token:
            return json.dumps({"error": "Token ID is missing"})

        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        if member:
            if member.token:
                member.sudo().write({
                    'token': token,
                })
                return json.dumps({'Member Firebase Token Updated': member.membership_no})
            else:
                member.sudo().write({
                    'token': token,
                })
                return json.dumps({'Member Firebase Token Created': member.membership_no})
        else:
            return json.dumps({"error": "Membership ID is mismatched"})
