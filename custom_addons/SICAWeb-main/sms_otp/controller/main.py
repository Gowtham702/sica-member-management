from odoo import http
from odoo.http import request
import json
import random
import requests
import uuid
from datetime import datetime, timedelta


class ResPartnerController(http.Controller):
    @http.route('/custom_api/get_res_partners', type='http', auth='public', methods=['GET'])
    def get_res_partners_id(self, **kw):
        partner_records = request.env['res.partner'].sudo().search_read([], ['name', 'email', 'phone'])
        return json.dumps(partner_records)



class LoginOtpRequest(http.Controller):

    @http.route('/otp/verify', type='http', auth='none', methods=['GET'], csrf=False)
    def action_otp_verify(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"

        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$", api_key)
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        else:
            otp = kw.get('OTP')
            access_token = kw.get('access_token')
            sms_otp = request.env['sms.otp'].sudo().search([('otp_number', '=', otp), ('access_token', '=', access_token)], limit=1)

            if sms_otp:
                otp_validity_duration = timedelta(minutes=2)
                current_time = datetime.now()
                time_difference = current_time - sms_otp.create_date
                if time_difference > otp_validity_duration:
                    return json.dumps({"error": "Invalid OTP or Expired"})
                else:
                    sms_otp.write({'is_session_status': "Open"})
                    return json.dumps({"verification": "Success"})
            else:
                return json.dumps({"error": "Invalid OTP"})

    @http.route('/member/session/close', type='http', auth='none', methods=['POST'], csrf=False)
    def action_member_close_session(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        else:
            access_token = kw.get('access_token')
            membership_number = kw.get('membership_number')
            sms_session = request.env['sms.otp'].sudo().search(
                [('membership_number', '=', membership_number), ('access_token', '=', access_token)], limit=1)
            if sms_session:
                sms_session.write({'is_session_status': "Close"})
                return json.dumps({"Session": "Closed"})
            else:
                return json.dumps({"Access Token Wrong": "Wrong"})



    @http.route('/api/get_login_otp', type='http', auth='none', methods=['GET'])
    def get_res_partners(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        mobile_number = kw.get('MOBILE_NUMBER')
        membership_id = kw.get('MEMBERSHIP_ID')
        guest_name = kw.get('guest_name')
        access_token = str(uuid.uuid4())
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        account_type = kw.get('account_type')
        if not account_type:
            create_otp_master = request.env['sms.otp'].create({
                'account_type': 'member',
                'otp_number': '',
                'guest_name': guest_name,
                'mobile_number': mobile_number,
                'membership_number': membership_id,
                'return_value': 'ACCOUNT TYPE MISSING',
                'access_token': access_token,
                'is_session_status': "Request_Sent"
            })
            return json.dumps({'error': 'ACCOUNT TYPE MISSING'})
        otp_length = 4
        # Generate a random OTP
        otp = ""
        for i in range(otp_length):
            otp += str(random.randint(0, 4))
        if account_type == 'GUEST':
            mobile_number = kw.get('MOBILE_NUMBER')
            if not mobile_number:
                create_otp_master = request.env['sms.otp'].create({
                    'account_type': 'guest',
                    'otp_number': otp,
                    'mobile_number': mobile_number,
                    'membership_number': membership_id,
                    'return_value': 'MOBILE NUMBER IS REQUIRED',
                    'access_token': access_token,
                    'guest_name': guest_name,
                    'is_session_status': "Request_Sent"
                })

                return json.dumps({'error': 'MOBILE NUMBER IS REQUIRED'})
            # post_url = "http://pay4sms.in/sendsms/?token=83ba323c7d09c429d81666aaacb224bb&credit=2&sender=SICAMS&message=Dear%20Member,%20your%20OTP%20for%20SICA%20App%20registration%20is%20{}.%20Please%20do%20not%20share%20it%20with%20anyone.&number={}".format(
            #     otp,mobile_number)
            post_url = "http://bhashsms.com/api/sendmsg.php?user=Think42labs&pass=123456&sender=23122&phone={}&text=sica_otp&priority=wa&stype=auth&Params={}".format(
                mobile_number,otp)
            post_result = requests.post(post_url)
            if post_result.status_code == 200:  # Assuming a successful response
                post_return = post_result.text
                if 'S' in post_return:
                    create_otp_master = request.env['sms.otp'].create({
                        'account_type': 'guest',
                        'otp_number': otp,
                        'mobile_number': mobile_number,
                        'membership_number': membership_id,
                        'return_value': post_return,
                        'access_token': access_token,
                        'guest_name': guest_name,
                        'is_session_status': "Request_Sent"
                    })
                    return json.dumps({'account_type': 'GUEST', 'OTP': otp, 'access_token': access_token, 'success': "Yes"})
                else:
                    create_otp_master = request.env['sms.otp'].create({
                        'account_type': 'guest',
                        'otp_number': otp,
                        'mobile_number': mobile_number,
                        'membership_number': membership_id,
                        'return_value': post_return,
                        'access_token': access_token,
                        'guest_name': guest_name,
                        'is_session_status': "Request_Sent"
                    })
                    return json.dumps(
                        {'account_type': 'GUEST', 'OTP': otp, 'access_token': access_token, 'success': "No"})
            else:
                create_otp_master = request.env['sms.otp'].create({
                    'account_type': 'guest',
                    'otp_number': otp,
                    'mobile_number': mobile_number,
                    'membership_number': membership_id,
                    'return_value': post_result.status_code,
                    'access_token': access_token,
                    'guest_name': guest_name,
                    'is_session_status': "Request_Sent"
                })
                return json.dumps({'error': post_result.status_code, 'success': "No"})

        if account_type == 'MEMBER':
            membership_id = kw.get('MEMBERSHIP_ID')
            if not membership_id:
                create_otp_master = request.env['sms.otp'].create({
                    'account_type': 'member',
                    'otp_number': otp,
                    'membership_number': membership_id,
                    'return_value': 'MEMBERSHIP IS REQUIRED',
                    'access_token': access_token,
                    'is_session_status': "Request_Sent"
                })
                return json.dumps({'error': 'MEMBERSHIP IS REQUIRED'})
            mobile_number = kw.get('MOBILE_NUMBER')
            if not mobile_number:
                create_otp_master = request.env['sms.otp'].create({
                    'account_type': 'member',
                    'otp_number': otp,
                    'mobile_number': mobile_number,
                    'membership_number': membership_id,
                    'return_value': 'MOBILE NUMBER IS REQUIRED',
                    'access_token': access_token,
                    'is_session_status': "Request_Sent"
                })
                return json.dumps({'error': 'MOBILE NUMBER IS REQUIRED'})
            member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
            if member:
                membership_number = request.env['res.member'].sudo().search([('id', '=', member.id), '|', ('contact1', '=', mobile_number), ('contact2', '=', mobile_number)], limit=1)
                if not membership_number:
                    create_otp_master = request.env['sms.otp'].create({
                        'account_type': 'member',
                        'otp_number': otp,
                        'mobile_number': mobile_number,
                        'membership_number': membership_id,
                        'return_value': 'MOBILE NUMBER IS MISMATCHED',
                        'access_token': access_token,
                        'is_session_status': "Request_Sent"
                    })
                    return json.dumps({'error': 'MOBILE NUMBER IS MISMATCHED'})
            else:
                create_otp_master = request.env['sms.otp'].create({
                    'account_type': 'member',
                    'otp_number': otp,
                    'mobile_number': mobile_number,
                    'membership_number': membership_id,
                    'return_value': 'MEMBERSHIP ID IS MISSING OR WRONG',
                    'access_token': access_token,
                    'is_session_status': "Request_Sent"
                })
                return json.dumps({'error': 'MEMBERSHIP ID IS MISSING OR WRONG'})
            # post_url = "http://pay4sms.in/sendsms/?token=83ba323c7d09c429d81666aaacb224bb&credit=2&sender=SICAMS&message=Dear%20Member,%20your%20OTP%20for%20SICA%20App%20registration%20is%20{}.%20Please%20do%20not%20share%20it%20with%20anyone.&number={}".format(
            #     otp, mobile_number)
            post_url = "http://bhashsms.com/api/sendmsg.php?user=Think42labs&pass=123456&sender=23122&phone={}&text=sica_otp&priority=wa&stype=auth&Params={}".format(
                mobile_number, otp)
            post_result = requests.post(post_url)
            if post_result.status_code == 200:  # Assuming a successful response
                post_return = post_result.text
                if 'S' in post_return:
                    create_otp_master = request.env['sms.otp'].create({
                        'member_id': member.id,
                        'account_type': 'member',
                        'otp_number': otp,
                        'membership_number': membership_id,
                        'mobile_number': mobile_number,
                        'return_value': post_return,
                        'access_token': access_token,
                        'is_session_status': "Request_Sent"
                    })
                    return json.dumps(
                        {'account_type': 'MEMBER', 'OTP': otp, 'access_token': access_token, 'success': "Yes"})

                else:
                    create_otp_master = request.env['sms.otp'].create({
                        'member_id': member.id,
                        'account_type': 'member',
                        'otp_number': otp,
                        'membership_number': membership_id,
                        'mobile_number': mobile_number,
                        'return_value': post_return,
                        'access_token': access_token,
                        'is_session_status': "Request_Sent"
                    })
                    return json.dumps(
                        {'account_type': 'MEMBER', 'OTP': otp, 'access_token': access_token, 'success': "No"})
            else:
                create_otp_master = request.env['sms.otp'].create({
                    'member_id': member.id,
                    'account_type': 'member',
                    'otp_number': otp,
                    'mobile_number': mobile_number,
                    'membership_number': membership_id,
                    'return_value': post_result.status_code,
                    'access_token': access_token,
                    'is_session_status': "Request_Sent"
                })
                return json.dumps(
                    {'account_type': 'MEMBER', 'OTP': otp, 'access_token': access_token, 'success': "No"})

