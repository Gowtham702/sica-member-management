from odoo import http
from odoo.http import request
import json
import random
import requests
import datetime
from datetime import datetime
import razorpay
import math


class ActionCreateRazorpayPaid(http.Controller):
    @http.route('/member/payment_information/<string:membership_no>', type='http', auth='none', methods=['GET'],
                csrf=False)
    def action_get_member_payment_information(self, membership_no, **kw):
        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_no)])
        member_payment_details = []
        current_year = datetime.now().year
        paid_till = int(member.paid_till)
        subscription_years = []
        penalty_fee = float(request.env['ir.config_parameter'].sudo().get_param('member_management_system.penalty_fee'))
        gateway_note = request.env['ir.config_parameter'].sudo().get_param('member_management_system.payment_gateway_notes')
        subscription_fee = 0.0
        sica_fee = 0.0
        cbt_fee = 0.0
        convenience_fee = 0.0
        penalty = 0.0

        count = 0
        if not current_year - 3 > paid_till:
            for i in range(paid_till, current_year):
                count += 1
                penalty_amount = 0
                subscription_fee += member.cbt_fee + member.sica_fee
                if i + 1 == current_year:
                    sica_fee += member.sica_fee
                    cbt_fee += member.cbt_fee
                else:
                    if member.cbt_fee:
                        sica_fee += member.cbt_fee + penalty_fee
                        penalty_amount += penalty_fee
                    if member.sica_fee:
                        sica_fee += member.sica_fee + penalty_fee
                        penalty_amount += penalty_fee

                years = {
                    'year': i + 1,
                    'cbt_amount': member.cbt_fee,
                    'sica_fee': member.sica_fee,
                    'subscription_amount': member.sica_fee + member.cbt_fee,
                    'penalty': penalty_amount
                }
                subscription_years.append(years)
                penalty += penalty_amount
            total_sica_cbt = sica_fee + cbt_fee
            platform_fee = total_sica_cbt * 2/100
            platform_gst = platform_fee * 18/100
            convenience_fee += platform_fee + platform_gst
            if cbt_fee:
                trans_fee = cbt_fee * 0.25/100
                trans_fee_gst = trans_fee * 18/100
                convenience_fee += trans_fee + trans_fee_gst
            convenience_fee = (convenience_fee + total_sica_cbt) * 0.096/100 + convenience_fee
            convenience_fee = int(math.ceil(convenience_fee))
            total_fee = penalty + subscription_fee + int(math.ceil(convenience_fee))
            member_payment_details.append({
                'subscription_years': subscription_years or '',
                'subscription_total_fee': subscription_fee,
                'total_fee': total_fee,
                'penalty_fee': penalty or 0.0,
                'gateway_note': gateway_note or '',
                'paid_till': member.paid_till,
                'is_member_debar': member.state == 'debar',
                'convience_fee': convenience_fee
            })
        else:
            member_payment_details.append({
                'is_member_debar': True,
                'gateway_note': "Please Contact SICA Administration",
            })

        return json.dumps({
            'member_payment_details': member_payment_details
        })


    @http.route('/razorpay/split', type='json', auth='none', methods=['POST'], csrf=False)
    def action_transfer_amount_from_payment(self):
        # Initialize the Razorpay client
        key_id = 'rzp_live_XJAsIy7cyVctJb'
        key_secret = 'xbFvM32bITRHSQ5qsMeFX6BD'
        client = razorpay.Client(auth=(key_id, key_secret))

        # Specify the payment ID
        payment_id = "pay_E8JR8E0XyjUSZd"

        # Specify the transfer details
        transfer_data = {
            "transfers": [
                {
                    "account": 'acc_HgzcrXeSLfNP9U',
                    "amount": 100,
                    "currency": "INR",
                    "notes": {
                        "name": "Gaurav Kumar",
                        "roll_no": "IEC2011025"
                    },
                    "linked_account_notes": [
                        "branch"
                    ],
                    "on_hold": 1,
                    "on_hold_until": 1671222870
                }
            ]
        }

        # Initiate the transfer
        response = client.payment.transfer(payment_id, transfer_data)

        # Print the transfer response
        print(response)

    @http.route('/razorpay/paid', type='json', auth='none', methods=['POST', 'GET'], csrf=False)
    def action_razorpay_paid(self, **kw):
        # Assuming that the JSON request contains the necessary data
        json_data = request.jsonrequest
        print(json_data, 'Paid RazorPay')
        amount_paid = json_data['payload']['payment_link']['entity']['amount_paid']
        order_id = json_data['payload']['order']['entity']['id']
        print(order_id, 'Order ID')
        order_amount = json_data['payload']['order']['entity']['amount']
        print(order_amount, 'Order Amount')
        payment_link_id = json_data['payload']['payment_link']['entity']['id']
        print(payment_link_id, 'Payment link')
        payment_link_url = json_data['payload']['payment_link']['entity']['short_url']
        print(payment_link_url, 'Payment link Url ')
        status = json_data['payload']['payment_link']['entity']['status']
        member_id = json_data['payload']['payment_link']['entity']['notes']['member_id']
        print(status, 'Status')
        amount = float(amount_paid/100)
        print(amount, 'Amount Paid')


        member_payment = request.env['member.payment'].sudo().create({
            'order_id': order_id,
            'order_amount': order_amount,
            'payment_link_id': payment_link_id,
            'payment_link_url': payment_link_url,
            'payment_status': status,
            'amount_paid': amount,
            'note': json_data
        })
        member_payment.write({'member_id': int(member_id)})

        # Your logic for handling the Razorpay payment with the JSON data

        return json.dumps({'status': 'success'})


class ActionCreateRazorpayOrder(http.Controller):
    @http.route('/create/razorpay_order', type='http', auth='none', methods=['GET'], csrf=False)
    def action_create_razorpay_order(self, **kw):
        key_id = 'rzp_live_XJAsIy7cyVctJb'
        key_secret = 'xbFvM32bITRHSQ5qsMeFX6BD'
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        client = razorpay.Client(auth=(key_id, key_secret))
        membership_id = kw.get('MEMBERSHIP_ID')
        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        current_year = datetime.now().year
        paid_till = int(member.paid_till)
        penalty_fee = float(request.env['ir.config_parameter'].sudo().get_param('member_management_system.penalty_fee'))
        total_fee = 0.0
        count = 0
        sica_fee = 0.0
        cbt_fee = 0.0
        convenience_fee = 0.0
        penalty = 0.0
        if not current_year - 3 > paid_till:
            for i in range(paid_till, current_year):
                count += 1
                penalty_amount = 0
                if i + 1 == current_year:
                    sica_fee += member.sica_fee
                    cbt_fee += member.cbt_fee
                else:
                    if member.cbt_fee:
                        sica_fee += member.cbt_fee + penalty_fee
                        penalty_amount += penalty_fee
                    if member.sica_fee:
                        sica_fee += member.sica_fee + penalty_fee
                        penalty_amount += penalty_fee
                penalty += penalty_amount
            total_sica_cbt = sica_fee + cbt_fee
            platform_fee = total_sica_cbt * 2 / 100
            platform_gst = platform_fee * 18 / 100
            convenience_fee += platform_fee + platform_gst
            if cbt_fee:
                trans_fee = cbt_fee * 0.25 / 100
                trans_fee_gst = trans_fee * 18 / 100
                convenience_fee += trans_fee + trans_fee_gst
            convenience_fee = (convenience_fee + total_sica_cbt) * 0.096 / 100 + convenience_fee
            total_fee = total_sica_cbt + convenience_fee
            razorpay_amount = int(math.ceil(total_fee)) * 100
        resulrt = client.payment_link.create({
            "amount": razorpay_amount or 100,
            "currency": "INR",
            "accept_partial": False,
            "description": "For SICA Subscription",
            "customer": {
                "name": member.name,
                "email": member.email or 'muthaiyanselvam01@gmail.com',
                # "contact": member.contact1
            },
            "notify": {
                "sms": 'false',
                "email": 'false'
            },
            "reminder_enable": 'false',
            "notes": {
                "policy_name": "Subscription",
                'member_id': member.id
            },
            "callback_url": "https://www.thesica.in/",
            "callback_method": "get"
        })
        # return json.dumps({'Order_id': result})
        print(resulrt, 'Payment link resultt')
        print(resulrt.get('short_url'), 'Payment Url')
        member_payment_request = request.env['member.payment.request'].sudo().create({
            'membership_no': membership_id,
            'member_name': member.name,
            'amount': total_fee,
            'payment_link': resulrt.get('short_url'),
            'contact_no': member.contact1,
            'note': resulrt,
            'member_id': member.id
        })
        return json.dumps({"payment link": resulrt})
