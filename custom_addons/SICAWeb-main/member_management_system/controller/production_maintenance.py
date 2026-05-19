from odoo import http, fields
from odoo.http import request
import json
import random
import requests

class SicaProduction(http.Controller):
    @http.route('/get/app/maintenance', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_maintenance_version(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"

        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        maintenance = request.env['ir.config_parameter'].sudo().get_param('member_management_system.under_maintenance')
        if maintenance:
            return json.dumps({"Maintenance": "Required"})
        else:
            return json.dumps({"Maintenance": "Not Required"})

    @http.route('/get/app/version', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_app_version(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"

        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        app_version = request.env['ir.config_parameter'].sudo().get_param('member_management_system.app_update')
        if app_version:
            return json.dumps({"Current Version": app_version})
        else:
            return json.dumps({"App Version": "Not Captured"})


