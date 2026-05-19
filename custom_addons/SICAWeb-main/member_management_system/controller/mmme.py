import base64
import re
from odoo import http, fields
from odoo.http import request, Response
import json
import random
import requests
import time,pytz
from datetime import datetime,timedelta,timezone,date
from dateutil.relativedelta import relativedelta


class MyMovieMyExperience(http.Controller):


    @http.route('/get/mymoviemyexperience', type='http', auth='public', methods=['GET'], csrf=False)
    def action_get_myexperience(self, **kw):
        try:
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url.image')
            if not base_url:
                base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if not base_url:
                return Response(json.dumps({"error": "Base URL is not configured on the server."}), content_type='application/json')

            api_key = kw.get('api_key')
            stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"

            if not api_key:
                return Response(json.dumps({"error": "API key is missing"}), content_type='application/json')
            if api_key != stored_api_key:
                return Response(json.dumps({"error": "Invalid API key"}), content_type='application/json')

            mmme_details = []
            mmme_vals = request.env['mymovie.myexperience'].sudo().search([('state', '=', 'approved')], order="sequence asc")

            for mmme in mmme_vals:
                image_base64 = mmme.image or ''
                if image_base64:
                    image_base64 = image_base64.decode("utf-8") if isinstance(image_base64, bytes) else image_base64

                description_html = mmme.description or ''
                if description_html:
                    # Fix relative image URLs in description HTML
                    description_html = re.sub(
                        r'src=[\'"](/web/content[^\'"]+)[\'"]',
                        f'src="{base_url}\\1"',
                        description_html
                    )

                vals = {
                    'title': mmme.title or '',
                    'date': mmme.date.strftime("%Y-%m-%d") if mmme.date else '',
                    'views': mmme.views or 0,
                    'description': description_html,
                    'image_url': image_base64,
                }
                mmme_details.append(vals)

            response_data = {'My Movie My Experience': mmme_details}
            return Response(json.dumps(response_data), content_type='application/json')

        except Exception as e:
            error_response = {"error": f"Server Error: {str(e)}"}
            return Response(json.dumps(error_response), content_type='application/json')


    # @http.route('/get/mymoviemyexperience', type='http', auth='public', methods=['GET'], csrf=False)
    # def action_get_myexperience(self, **kw):

    #     try:
    #         # Get base URL
    #         base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url.image')
    #         if not base_url:
    #             base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #         if not base_url:
    #             return json.dumps({"error": "Base URL is not configured on the server."})

    #         # Validate API key
    #         api_key = kw.get('api_key')
    #         stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"

    #         if not api_key:
    #             return json.dumps({"error": "API key is missing"})
    #         if api_key != stored_api_key:
    #             return json.dumps({"error": "Invalid API key"})

    #         # Fetch approved records
    #         mmme_details = []
    #         mmme_vals = request.env['mymovie.myexperience'].sudo().search(
    #             [('state', '=', 'approved')],
    #             order="sequence asc"
    #         )

    #         for mmme in mmme_vals:
    #             # Main image URL
    #             image_url = f"{base_url}/web/image/mymovie.myexperience/{mmme.id}/image"

    #             # Fix image URLs in description
    #             description_html = mmme.description or ''
    #             print("1111111111111111111111111111111111111111111111111")
    #             # print(description_html)
    #             if description_html:
    #                 # Replace src="/web/content... with absolute URL
    #                 description_html = re.sub(
    #                     r'src=[\'"](/web/content[^\'"]+)[\'"]',
    #                     f'src=\"{base_url}\\1\"',
    #                     description_html
    #                 )
    #             print("description_html: ",description_html)
    #             vals = {
    #                 'title': mmme.title or '',
    #                 'date': mmme.date.strftime("%Y-%m-%d") if mmme.date else '',
    #                 'views': mmme.views or 0,
    #                 'description': mmme.description or '',
    #                 'image_url': image_url,
    #             }
    #             mmme_details.append(vals)

    #         return json.dumps({'My Movie My Experience': mmme_details})

    #     except Exception as e:
    #         return json.dumps({"error": f"Server Error: {str(e)}"})
        # try:
        #     # Get base URL from config
        #     base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url.image')
        #     if not base_url:
        #         base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

        #     if not base_url:
        #         return json.dumps({"error": "Base URL is not configured on the server."})

        #     # Validate API key
        #     api_key = kw.get('api_key')
        #     stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"

        #     if not api_key:
        #         return json.dumps({"error": "API key is missing"})
        #     if api_key != stored_api_key:
        #         return json.dumps({"error": "Invalid API key"})

        #     # Fetch approved records
        #     mmme_details = []
        #     mmme_vals = request.env['mymovie.myexperience'].sudo().search(
        #         [('state', '=', 'approved')],
        #         order="sequence asc"
        #     )

        #     for mmme in mmme_vals:
        #         # Construct image URL
        #         image_url = f"{base_url}/web/image/mymovie.myexperience/{mmme.id}/image"
                
        #         # Optionally get base64 image data
        #         base64_string = ''
        #         if mmme.image:
        #             base64_string = base64.b64encode(mmme.image).decode('utf-8')

        #         # Build response values
        #         vals = {
        #             'title': mmme.title or '',
        #             'date': mmme.date.strftime("%Y-%m-%d") if mmme.date else '',
        #             'views': mmme.views or 0,
        #             'description': mmme.description or '',
        #             'image_url': image_url,
        #             # 'image_base64': base64_string  # Optional: include this if needed
        #         }
        #         mmme_details.append(vals)

        #     return json.dumps({'My Movie My Experience': mmme_details})

        # except Exception as e:
        #     # Log error for debugging (optional)
        #     # _logger.exception("Error in action_get_myexperience: %s", str(e))
        #     return json.dumps({"error": f"Server Error: {str(e)}"})

    # @http.route('/get/mymoviemyexperience', type='http', auth='public', methods=['GET'], csrf=False)
    # def action_get_myexperience(self, **kw):
    #     base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url.image')

    #     api_key = kw.get('api_key')  # Extract the API key from the GET parameters
    #     stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
    #     if not api_key:
    #         return json.dumps({"error": "API key is missing"})
    #     if api_key != stored_api_key:
    #         return json.dumps({"error": "Invalid API key"})

    #     mmme_details = []
    #     mmme_vals = request.env['mymovie.myexperience'].sudo().search([('state', '=', 'approved')], order="sequence asc")
    #     for mmme in mmme_vals:
    #         image = base_url + '/web/image?' + 'model=mymovie.myexperience&id=' + str(mmme.id) + '&field=image'
    #         base64_string = ''
    #         image_data = mmme.image
    #         if image_data:
    #             base64_string = base64.b64encode(image_data).decode('utf-8')
    #         vals = {
    #             'title': mmme.title or '',
    #             'date': mmme.date.strftime("%Y-%m-%d") if mmme.date else '',
    #             'views': mmme.views or 0,
    #             'description': mmme.description,
    #             'image_url': image
    #         }
    #         mmme_details.append(vals)
    #     return json.dumps({'My Movie My Experience': mmme_details})

    @http.route('/create/mmme_details/json', type="json", auth='none', methods=['POST'], csrf=False)
    def action_create_myexperience_json(self, **kw):
        print('✅ JSON API called')

        try:
            payload = request.httprequest.data.decode()
            payload = json.loads(payload)
        except Exception as e:
            return {"error": f"Invalid JSON payload: {str(e)}"}

        # API key validation
        api_key = payload.get('api_key')
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"

        if not api_key:
            return {"error": "API key is missing"}
        if api_key != stored_api_key:
            return {"error": "Invalid API key"}

        # Extract fields
        title = payload.get('title')
        date = payload.get('date')
        views = payload.get('views')
        description = payload.get('description')
        image_b64 = payload.get('image')

        # Prepare values
        vals = {
            'title': title,
            'date': date,
            'views': views,
            'description': description,
        }

        # Handle image if provided
        if image_b64:
            try:
                # Ensure valid base64
                base64.b64decode(image_b64, validate=True)
                vals['image'] = image_b64  # Directly store base64 data (Odoo supports this)
            except Exception:
                return {"error": "Invalid base64 image data"}

        # Create record
        record = request.env['mymovie.myexperience'].sudo().create(vals)

        return {
            'success': True,
            'message': 'My Movie Experience created successfully',
            'id': record.id
        }
