# -*- coding: utf-8 -*-
from odoo import http, fields, _
from odoo.http import request
import json
import base64

class MobilePushNotificationAPI(http.Controller):

    @http.route('/public/image/<int:record_id>', auth='public')
    def public_notification_image(self, record_id, **kwargs):
        record = request.env['mobile.app.push.notification'].sudo().browse(record_id)
        if not record or not record.image:
            return request.not_found()

        image_data = record.image
        headers = [
            ('Content-Type', 'image/png'),
            ('Content-Length', str(len(image_data))),
        ]
        return request.make_response(image_data, headers)

    # ---------------------------------------------------------
    # API: Send Push Notification
    # ---------------------------------------------------------
    @http.route('/api/send/push/notification',
                type='json', auth='none', methods=['POST'], csrf=False)
    def send_push_notification_api(self, **kw):

        # ---------------------------------------------
        # PARSE RAW JSON
        # ---------------------------------------------
        try:
            raw_data = request.httprequest.data.decode()
            payload = json.loads(raw_data)
        except Exception as e:
            return {
                "status": "error",
                "message": "Invalid JSON format",
                "details": str(e)
            }

        # ---------------------------------------------
        # API KEY VALIDATION
        # ---------------------------------------------
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"

        api_key = payload.get('api_key')
        if not api_key:
            return {"status": "error", "message": "API key missing"}

        if api_key != stored_api_key:
            return {"status": "error", "message": "Invalid API key"}

        # ---------------------------------------------
        # READ FIELDS
        # ---------------------------------------------
        title = payload.get('title')
        message = payload.get('message')
        send_to = payload.get('send_to', 'to_all')
        membership_nos = payload.get('membership_nos')
        image_base64 = payload.get('image_base64')
        links = payload.get('links')
        image_link = payload.get('image_link')

        if not title or not message:
            return {"status": "error", "message": "title and message are required"}

        # ---------------------------------------------
        # MEMBER LOOKUP (SINGLE / MULTIPLE)
        # ---------------------------------------------
        member_ids = []

        if send_to == "to_specefic":

            if not membership_nos:
                return {
                    "status": "error",
                    "message": "membership_nos is required for send_to='to_specefic'"
                }

            # Accept comma-separated string
            if isinstance(membership_nos, str):
                membership_list = [m.strip() for m in membership_nos.split(",") if m.strip()]

            # Accept list
            elif isinstance(membership_nos, list):
                membership_list = membership_nos

            else:
                return {
                    "status": "error",
                    "message": "membership_nos must be a string or list"
                }

            # Search members
            members = request.env['res.member'].sudo().search([
                ('membership_no', 'in', membership_list)
            ])

            if not members:
                return {
                    "status": "error",
                    "message": f"No members found for membership_nos: {membership_list}"
                }

            member_ids = members.ids

        # ---------------------------------------------
        # PREPARE VALUES FOR RECORD CREATION
        # ---------------------------------------------
        vals = {
            "name": title,
            "body": message,
            "send_notification_to": send_to,
            "links": links,
            "image_link": image_link,
        }

        # Apply M2M
        if send_to == "to_specefic":
            vals["member_ids"] = [(6, 0, member_ids)]
        else:
            vals["member_ids"] = [(5, 0, 0)]  # clear

        # ---------------------------------------------
        # SAVE IMAGE IF PROVIDED
        # ---------------------------------------------
        if image_base64:
            try:
                base64.b64decode(image_base64)  # validate
                vals["image"] = image_base64
            except Exception:
                return {
                    "status": "error",
                    "message": "Invalid Base64 image data"
                }

        # ---------------------------------------------
        # CREATE NOTIFICATION RECORD
        # ---------------------------------------------
        notification = request.env['mobile.app.push.notification'].sudo().create(vals)

        # ---------------------------------------------
        # SEND NOTIFICATION
        # ---------------------------------------------
        try:
            result = notification.sudo().send_notification()
        except Exception as e:
            return {
                "status": "error",
                "message": f"Send failed: {str(e)}"
            }

        # ---------------------------------------------
        # SUCCESS RESPONSE
        # ---------------------------------------------
        return {
            "status": "success",
            "notification_id": notification.id,
            "sent_to_member_ids": member_ids,
            "summary": result.get("params", {}).get("message"),
            "state": notification.state,
            "image_saved": True if image_base64 else False,
        }

    # ---------------------------------------------------------
    # API: Get Notification Logs
    # ---------------------------------------------------------
    @http.route('/api/notification/logs',
                type='json', auth='none', methods=['GET'], csrf=False)
    def get_notification_logs(self, **kw):
        api_key = kw.get("api_key")
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"

        if not api_key:
            return {"error": "API key missing"}
        if api_key != stored_api_key:
            return {"error": "Invalid API key"}

        logs = request.env['push.notification.log.partner'].sudo().search([], limit=50)

        data = []
        for log in logs:
            data.append({
                "notification_id": log.notification_id.id,
                "member_id": log.member_id.id,
                "member_name": log.member_id.name,
                "date_send": str(log.date_send) if log.date_send else '',
                "status": log.notification_state,
            })

        return {"logs": data}
