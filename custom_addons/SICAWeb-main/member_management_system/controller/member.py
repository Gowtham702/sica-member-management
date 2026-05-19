import json
from odoo import http
from odoo.http import request, Response
from odoo import http, fields
from firebase_admin import messaging
from firebase_admin.messaging import UnregisteredError
import json
import logging

_logger = logging.getLogger(__name__)


class MemberAPI(http.Controller):

    @http.route('/api/members/names', type='http', auth='public', methods=['GET'])
    def get_members_names(self):
        members = request.env['res.member'].search([])
        data = [{'id': m.id, 'name': m.name} for m in members]
        return Response(json.dumps({'members': data}), content_type='application/json', status=200)

    @http.route('/api/members/grades', type='http', auth='public', methods=['GET'])
    def get_members_grades(self):
        members = request.env['res.member'].search([])
        data = [{'id': m.id, 'grade': m.grade} for m in members]
        return Response(json.dumps({'members': data}), content_type='application/json', status=200)
    

    @http.route('/api/members/names_notification/', type='http', auth='public', methods=['GET'], csrf=False)
    def get_data_to_frontend_mail(self,**kw):
        print("sakkthi")
        try:
            member_id = kw.get("id")
            print("111111111111111111111111111111111111111111")
            print(member_id)
            member_id = payload.get("id")  # Expecting JSON like {"member_id": 5}
            
            if not member_id:
                return http.Response(json.dumps({'error': 'member_id required'}),
                                     content_type='application/json', status=400)

            member = request.env['res.member'].sudo().browse(member_id)
            if not member.exists():
                return http.Response(json.dumps({'error': 'Member not found'}),
                                     content_type='application/json', status=404)

            if not member.token:
                return http.Response(json.dumps({'error': 'Member has no push token'}),
                                     content_type='application/json', status=400)

            # Prepare notification
            title = "Hello from the System"
            body = f"Hi {member.name}, you have a new notification!"
            send_url = f"https://app.thesica.in/members/{member.id}"

            # Send the push
            try:
                message = messaging.Message(
                    token=member.token,
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    data={"url": send_url}
                )
                response = messaging.send(message)
                _logger.info(f"Push sent to member {member.name}: {response}")
            except UnregisteredError:
                _logger.warning(f"Unregistered token for {member.name}")
                member.token = False
                return http.Response(json.dumps({'error': 'Unregistered token'}),
                                     content_type='application/json', status=400)
            except Exception as e:
                _logger.error(f"Failed to send push to {member.name}: {str(e)}")
                return http.Response(json.dumps({'error': str(e)}),
                                     content_type='application/json', status=500)

            return http.Response(json.dumps({'success': True}),
                                 content_type='application/json', status=200)

        except Exception as e:
            _logger.error(f"Error processing push notification: {str(e)}")
            return http.Response(json.dumps({'error': str(e)}),
                                 content_type='application/json', status=500)