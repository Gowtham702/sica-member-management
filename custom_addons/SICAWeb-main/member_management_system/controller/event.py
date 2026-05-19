from odoo import http, fields
from odoo.http import request
import json
import base64
import random
import requests
import datetime
from datetime import datetime
import razorpay
import time,pytz
from datetime import datetime,timedelta,timezone,date
from dateutil.relativedelta import relativedelta

class ShootingEvent(http.Controller):

    @http.route('/get/complete_event/image/<int:complete_event_id>', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_complete_event_image(self, complete_event_id, **kw):
        complete_event = request.env['event.complete.image'].sudo().search([('id', '=', complete_event_id)], limit=1)
        if complete_event and complete_event.image:
            image_base64 = base64.b64decode(complete_event.image)
            headers = [('Content-Type', 'image/jpeg')]
            return request.make_response(image_base64, headers)
        else:
            event_image_default_url = request.env['ir.config_parameter'].sudo().get_param('website.event_image_link')
            if event_image_default_url:
                return request.redirect(event_image_default_url)
            return request.not_found()


    @http.route('/get/new/event', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_new_event(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url.image')
        event_image_default_url = request.env['ir.config_parameter'].sudo().get_param('website.event_image_link')
        today = fields.Date.today()
        yesterday = today - relativedelta(days=1)
        new_events = request.env['shooting.event'].sudo().search([('create_date', '>=', yesterday),('create_date', '<=', today)])
        today_event_details = []
        for event in new_events:
            attachments = []
            event_links = [{'link': link.link} for link in event.event_links_ids]
            for attachment in event.attachments_ids:
                attachment.public = True
                attachments.append(base_url + '/web/image/%s' % attachment.id)
            image = base_url + '/web/image?' + 'model=shooting.event&id=' + str(
                event.id) + '&field=image'
            if not attachments:
                attachments.append(event_image_default_url)
            today_event_details.append({
                'title': event.title or '',
                'description': event.description or '',
                'start_date': event.start_date.strftime("%Y-%m-%d") if event.start_date else '',
                'end_date': event.end_date.strftime("%Y-%m-%d") if event.end_date else '',
                'coach_name': event.coach_name or '',
                'amount': event.amount or 0.0,
                'event_id': event.id,
                'image_url': image or '',
                'event_link': event.event_link or '',
                'is_completed': event.is_completed,
                'venue': event.venue or '',
                'time': event.time or '',
                'map': event.map or '',
                'program_presenters': event.program_presenters or '',
                'presised_by': event.presised_by or '',
                'chief_guest': event.chief_guest or '',
                'note': event.note or '',
                'images_url': attachments,
                'is_member_booked': True if event.booking_status_ids.filtered(lambda x: x.member_id.membership_no == member_number and x.booking_status =='Booked') else False,
                'event_links': event_links,
            })
        return json.dumps({'today_event_details': today_event_details})

    @http.route('/get/member/payment/reminder', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_new_payment_reminder(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        member_number = kw.get('member_number')
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        payment_reminder = request.env['res.member'].sudo().search([('paid_till', '=', 2023), ('membership_no', '=', member_number)])
        payment_reminder_details = []
        for member in payment_reminder:
            payment_reminder_details.append({
                'name': member.name or '',
                'membership_no': member.membership_no or '',
                'sica_fee': member.sica_fee or '',
                'cbt_fee': member.cbt_fee or '',
            })
        return json.dumps({'payment_reminder_details': payment_reminder_details})

    @http.route('/get/all/event/category', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_event_category(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        event_category_ids = request.env['event.category'].sudo().search([])
        category_details = []
        for category in event_category_ids:
            category_details.append({
                'category_name': category.name or '',
                'category_id': category.id,
            })
        return json.dumps({'event_category_details': category_details})

    @http.route('/get/all/events', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_all_events(self, **kw):
        api_key = kw.get('api_key')
        member_number = kw.get('member_number')
        event_image_default_url = request.env['ir.config_parameter'].sudo().get_param('website.event_image_link')
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url.image')
        # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        event_ids = request.env['shooting.event'].sudo().search([], order="sequence asc")
        event_details = []
        for event in event_ids:
            attachments = []
            event_status = []
            complete_event_ids = []
            complete_event_attachments = []
            event_links = [{'link': link.link} for link in event.event_links_ids]
            for attachment in event.attachments_ids:
                attachment.public = True
                attachments.append(base_url + '/web/image/%s' % attachment.id)
            image = base_url + '/web/image?' + 'model=shooting.event&id=' + str(
                event.id) + '&field=image'
            if not attachments:
                attachments.append(event_image_default_url)
            for member_event in event.booking_status_ids:
                vals = {
                    'member_id': member_event.member_id.id,
                    'event_id': member_event.event_id.id,
                    'event_title': member_event.event_id.title,
                    'event_amount': member_event.event_id.amount,
                    'payment_status': member_event.payment_status,
                    'booking_status': member_event.booking_status,
                    # 'event_book_id': member_event.id
                    'event_book_id': member_event.id,
                }
                event_status.append(vals)

            for complete_event in event.complete_event_ids:
                if complete_event.image:
                    complete_event_attachments.append(base_url + '/get/complete_event/image/%s' % complete_event.id)
                for attachment in complete_event.attachments_ids:
                    attachment.public = True
                    complete_event_attachments.append(base_url + '/web/image/%s' % attachment.id)
                if not complete_event_attachments:
                    complete_event_attachments.append(event_image_default_url)

                vals = {
                    'event_id': complete_event.event_id.id,
                    'complete_event_images_url': complete_event_attachments,
                }
                complete_event_ids.append(vals)

            event_details.append({
                'title': event.title or '',
                'description': event.description or '',
                'start_date': event.start_date.strftime("%Y-%m-%d") if event.start_date else '',
                'end_date': event.end_date.strftime("%Y-%m-%d") if event.end_date else '',
                'coach_name': event.coach_name or '',
                'amount': event.amount or 0.0,
                'event_id': event.id,
                'image_url': image or '',
                'event_link': event.event_link or '',
                'is_completed': event.is_completed,
                'venue': event.venue or '',
                'time': event.time or '',
                'map': event.map or '',
                'program_presenters': event.program_presenters or '',
                'presised_by': event.presised_by or '',
                'chief_guest': event.chief_guest or '',
                'note': event.note or '',
                'images_url': attachments,
                'booking_status': event_status or '',
                'complete_event_details': complete_event_ids or '',
                'is_member_booked': True if event.booking_status_ids.filtered(lambda x: x.member_id.membership_no == member_number and x.booking_status =='Booked') else False,
                'event_links': event_links,
            })
        return json.dumps({'event_details': event_details})

    @http.route('/get/all/category/events', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_category_based_events(self, **kw):
        api_key = kw.get('api_key')
        category_id = kw.get('category_id')
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url.image')
        # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        event_image_default_url = request.env['ir.config_parameter'].sudo().get_param('website.event_image_link')
        event_ids = request.env['shooting.event'].sudo().search([('category_id', '=', int(category_id))])
        event_details = []
        for event in event_ids:
            attachments = []
            event_status = []
            complete_event_ids = []
            complete_event_attachments = []
            event_links = [{'link': link.link} for link in event.event_links_ids]

            for attachment in event.attachments_ids:
                attachment.public = True
                attachments.append(base_url + '/web/image/%s' % attachment.id)
            image = base_url + '/web/image?' + 'model=shooting.event&id=' + str(
                event.id) + '&field=image'
            if not attachments:
                attachments.append(event_image_default_url)

            for complete_event in event.complete_event_ids:
                for attachment in complete_event.attachments_ids:
                    attachment.public = True
                    complete_event_attachments.append(base_url + '/web/image/%s' % attachment.id)
                if not complete_event_attachments:
                    complete_event_attachments.append(event_image_default_url)

                vals = {
                    'event_id': complete_event.event_id.id,
                    'complete_event_images_url': complete_event_attachments,
                }
                complete_event_ids.append(vals)

            event_details.append({
                'title': event.title or '',
                'description': event.description or '',
                'start_date': event.start_date.strftime("%Y-%m-%d") if event.start_date else '',
                'end_date': event.end_date.strftime("%Y-%m-%d") if event.end_date else '',
                'coach_name': event.coach_name or '',
                'amount': event.amount or 0.0,
                'event_id': event.id or False,
                'image_url': image or '',
                'event_link': event.event_link or '',
                'venue': event.venue or '',
                'time': event.time or '',
                'map': event.map or '',
                'program_presenters': event.program_presenters or '',
                'presised_by': event.presised_by or '',
                'chief_guest': event.chief_guest or '',
                'note': event.note or '',
                'images_url': attachments,
                'is_completed': event.is_completed,
                'complete_event_details': complete_event_ids or '',
                'event_links': event_links,
            })
        return json.dumps({'event_details': event_details})

    @http.route('/get/event/payment_link', type='http', auth='none', methods=['GET'], csrf=False)
    def get_event_payment_link(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})

        key_id = 'rzp_live_XJAsIy7cyVctJb'
        key_secret = 'xbFvM32bITRHSQ5qsMeFX6BD'

        client = razorpay.Client(auth=(key_id, key_secret))
        membership_id = kw.get('MEMBERSHIP_ID')
        event_id = kw.get('event_id')
        event = request.env['shooting.event'].sudo().search([('id', '=', event_id)], limit=1)
        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        resulrt = client.payment_link.create({
            "amount": event.amount *100 or 1,
            "currency": "INR",
            "accept_partial": False,
            "description": "For Event",
            "customer": {
                "name": member.name,
                "email": member.email or 'muthaiyanselvam01@gmail.com',
                "contact": member.contact1
            },
            "notify": {
                "sms": 'false',
                "email": 'false'
            },
            "reminder_enable": 'false',
            "notes": {
                "policy_name": "Event Booking",
                'member_id': member.id,
                'event_id': event.id,
                'event_name': event.title,
            },
            "callback_url": "https://www.codingcrown.com/",
            "callback_method": "get"
        })
        # return json.dumps({'Order_id': result})
        print(resulrt, 'Payment link resultt')
        print(resulrt.get('short_url'), 'Payment Url')

        member_payment_request = request.env['member.payment.request'].sudo().create({
            'membership_no': membership_id,
            'member_name': member.name,
            'amount': event.amount * 100 or 1,
            'payment_link': resulrt.get('short_url'),
            'contact_no': member.contact1,
            'note': resulrt,
            'member_id': member.id,
            'event_id': event_id,
            'event_name': event.title
        })
        return json.dumps({"payment link": resulrt})

    @http.route('/event/payment/callback', type='http', auth='none', methods=['POST'], csrf=False)
    def get_event_payment_call_back(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})

        data = kw.get('data')
        data = data.replace("'", '"')
        data_dict = json.loads(data)
        event_id = data_dict.get('event_id') or ''
        payment_status = data_dict.get('payment_status') or ''
        booking_status = data_dict.get('booking_status') or ''
        membership_id = kw.get('MEMBERSHIP_ID')
        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)

        event_payment_id = request.env['event.payment'].sudo().create({
            'event_id': event_id,
            'payment_status': payment_status,
            'booking_status': booking_status,
            'member_id': member.id
        })
        return json.dumps({'Payment call back ': event_payment_id.id})

    @http.route('/member/event/status', type='http', auth='none', methods=['GET', 'POST'], csrf=False)
    def get_member_event_status(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')  # Corrected case for 'membership_id'
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url.image')
        event_image_default_url = request.env['ir.config_parameter'].sudo().get_param('website.event_image_link')
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})

        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})

        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        if not member:
            return json.dumps({"error": "Membership Not Valid"})

        event_status = []
        member_event_ids = request.env['event.payment'].sudo().search([('member_id', '=', member.id)])
        for member_event in member_event_ids:
            attachments = []

            for attachment in member_event.event_id.attachments_ids:
                attachment.public = True
                attachments.append(base_url + '/web/image/%s' % attachment.id)
            image = base_url + '/web/image?' + 'model=shooting.event&id=' + str(
                member_event.event_id.id) + '&field=image'
            if not attachments:
                attachments.append(event_image_default_url)

            vals = {
                'member_id': member.id,
                'event_id': member_event.event_id.id,
                'event_title': member_event.event_id.title,
                'event_amount': member_event.event_id.amount,
                'payment_status': member_event.payment_status,
                'booking_status': member_event.booking_status,
                # 'event_book_id': member_event.id
                'event_book_id': member_event.id,
                'title': member_event.event_id.title or '',
                'description': member_event.event_id.description or '',
                'start_date': member_event.event_id.start_date.strftime("%Y-%m-%d") if member_event.event_id.start_date else '',
                'end_date': member_event.event_id.end_date.strftime("%Y-%m-%d") if member_event.event_id.end_date else '',
                'coach_name': member_event.event_id.coach_name or '',
                'amount': member_event.event_id.amount or 0.0,
                'image_url': image or '',
                'event_link': member_event.event_id.event_link or '',
                'is_completed': member_event.event_id.is_completed,
                'venue': member_event.event_id.venue or '',
                'time': member_event.event_id.time or '',
                'map': member_event.event_id.map or '',
                'program_presenters': member_event.event_id.program_presenters or '',
                'presised_by': member_event.event_id.presised_by or '',
                'chief_guest': member_event.event_id.chief_guest or '',
                'note': member_event.event_id.note or '',
                'images_url': attachments,
                'is_booked': member_event.booking_status == 'Booked'
            }
            event_status.append(vals)
        return json.dumps({'member_event_status': event_status})

    @http.route('/event/booking/cancel', type='http', auth='none', methods=['POST'], csrf=False)
    def get_member_event_cancel(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"

        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        data = kw.get('data')
        data = data.replace("'", '"')
        data_dict = json.loads(data)
        event_book_id = data_dict.get('event_book_id') or ''
        reason = data_dict.get('reason') or ''
        member_payment_id = request.env['event.payment'].sudo().search([('id', '=', int(event_book_id))])
        member_payment_id.write({
            'reason': reason,
            'booking_status': 'Cancelled',
        })
        return json.dumps({
            'Booking Cancel': 'Successful'
        })

    @http.route('/get/all/completed/events', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_all_completed_events(self, **kw):
        api_key = kw.get('api_key')
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url.image')
        event_image_default_url = request.env['ir.config_parameter'].sudo().get_param('website.event_image_link')
        # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        event_ids = request.env['shooting.event'].sudo().search([('is_completed', '=', True)])
        event_details = []
        for event in event_ids:
            attachments = []
            event_status = []
            complete_event_ids = []
            complete_event_attachments = []
            event_links = [{'link': link.link} for link in event.event_links_ids]
            for attachment in event.attachments_ids:
                attachment.public = True
                attachments.append(base_url + '/web/image/%s' % attachment.id)

            image = base_url + '/web/image?' + 'model=shooting.event&id=' + str(
                event.id) + '&field=image'
            if not attachments:
                attachments.append(event_image_default_url)

            for complete_event in event.complete_event_ids:
                if complete_event.image:
                    complete_event_attachments.append(base_url + '/get/complete_event/image/%s' % complete_event.id)
                for attachment in complete_event.attachments_ids:
                    attachment.public = True
                    complete_event_attachments.append(base_url + '/web/image/%s' % attachment.id)
                if not complete_event_attachments:
                    complete_event_attachments.append(event_image_default_url)

                vals = {
                    'event_id': complete_event.event_id.id,
                    'complete_event_images_url': complete_event_attachments,
                }
                complete_event_ids.append(vals)

            event_details.append({
                'title': event.title or '',
                'description': event.description or '',
                'start_date': event.start_date.strftime("%Y-%m-%d") if event.start_date else '',
                'end_date': event.end_date.strftime("%Y-%m-%d") if event.end_date else '',
                'coach_name': event.coach_name or '',
                'amount': event.amount or 0.0,
                'event_id': event.id or False,
                'image': image or '',
                'event_link': event.event_link or '',
                'venue': event.venue or '',
                'time': event.time or '',
                'map': event.map or '',
                'program_presenters': event.program_presenters or '',
                'presised_by': event.presised_by or '',
                'chief_guest': event.chief_guest or '',
                'note': event.note or '',
                'complete_event_details': complete_event_ids or '',
                'images_url': attachments,
                'event_links': event_links
            })
        return json.dumps({'event_details': event_details})



