from odoo import http, fields
from odoo.http import request
import json
import datetime
from datetime import datetime


class ShootingTitle(http.Controller):
    @http.route('/create/shooting_title', type='http', auth='none', methods=['POST'], csrf=False)
    def action_create_shooting_title(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')  # Corrected case for 'membership_id'

        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})

        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        data = kw.get('data')
        data = data.replace("'", '"')
        data_dict = json.loads(data)
        title_name = data_dict.get('title_name') or ''
        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        shooting_title = request.env['shooting.title'].sudo().create({
            'name': title_name,
            'member_id': member.id,
        })
        return json.dumps({'Shooting Title': 'Shooting Title Creaed', 'ID': shooting_title.id})

    @http.route('/get/shooting_title', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_shooting_title(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')  # Corrected case for 'membership_id'

        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})

        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        shooting_title = request.env['shooting.title'].sudo().search([])
        shooting_titles = []
        for title in shooting_title:
            shooting_titles.append({
                'title': title.name,
                'id': title.id
            })

        return json.dumps({'Shooting Titles': shooting_titles})

    @http.route('/get/shooting_image', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_shooting_image(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url.image')

        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})

        shooting_image = request.env['shooting.image'].sudo().search([])
        shooting_image_details = []
        for image in shooting_image:
            shooting_image_details.append({
                'title': image.name,
                'image_url': base_url + '/web/image?' + 'model=shooting.image&id=' + str(image.id) + '&field=image' or '',
                'id': image.id
            })

        return json.dumps({'Shooting Image': shooting_image_details})


class Shooting(http.Controller):
    @http.route('/create/update_shooting', type='http', auth='none', methods=['POST'], csrf=False)
    def action_create_update_shooting(self, **kw):

        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')  # Corrected case for 'membership_id'

        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})

        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        data = kw.get('data')
        data = data.replace("'", '"')
        data_dict = json.loads(data)
        date = data_dict.get('date') or ''
        mobile_number = data_dict.get('mobile_number') or ''
        member_name = data_dict.get('member_name') or ''
        member_number = data_dict.get('member_number') or ''
        grade = data_dict.get('grade') or ''
        dop_name = data_dict.get('dop_name') or ''
        dop_member_number = data_dict.get('dop_member_number') or ''
        project_title = data_dict.get('project_title') or ''
        designation = data_dict.get('designation') or ''
        medium = data_dict.get('format_id') or ''
        producer = data_dict.get('producer') or ''
        production_house = data_dict.get('production_house') or ''
        production_executive = data_dict.get('production_executive') or ''
        production_executive_contact_no = data_dict.get('production_executive_contact_no') or ''
        location = data_dict.get('location') or ''
        outdoor_unit_name = data_dict.get('outdoor_unit_name') or ''
        notes = data_dict.get('notes') or ''
        # choose_dop_for_approval = data_dict.get('choose_dop_for_approval') or ''
        medium_id = request.env['member.medium'].sudo().search([('id', '=', int(medium))], limit=1)

        if membership_id == '':
            return json.dumps({"error": "Membership ID is mismatched"})
        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        dop_member = request.env['res.member'].sudo().search([('membership_no', '=', dop_member_number)], limit=1)
        shooting_title_id = request.env['shooting.title'].sudo().search([('name', '=', project_title)], limit=1)
        if not shooting_title_id:
            shooting_title_id = request.env['shooting.title'].sudo().create({
                'name': project_title,
                'member_id': member.id,
            })
        date_format = "%d/%m/%Y"
        if date == "":
            date = None
        else:
            date = datetime.strptime(date, date_format).date()
        sica_shooting = request.env['sica.shooting'].sudo().create({
            'date': date,
            'mobile_number': mobile_number,
            'member_id': member.id,
            'shooting_title_id': shooting_title_id.id,
            'member_name': member_name,
            'member_number': member_number,
            'grade': grade,
            'dop_name': dop_name,
            'dop_number': dop_member_number,
            'dop_member_id': dop_member.id or False,
            'designation': designation,
            'project_title': project_title,
            'medium': medium or '',
            'medium_id': medium_id.id or False,
            'producer': producer,
            'production_house': production_house,
            'production_executive': production_executive,
            'production_executive_contact_no': production_executive_contact_no,
            'location': location,
            'outdoor_unit_name': outdoor_unit_name,
            'notes': notes,
            'state': 'Waiting For Dop Approval'
        })

        return json.dumps({'Sica Shooting': 'Shooting Created', 'ID': sica_shooting.id})

    @http.route('/gat/member/update_shooting', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_update_shooting(self, **kw):

        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')  # Corrected case for 'membership_id'

        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})

        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        member_shooting = []
        if membership_id:
            member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
            update_shooing_ids = request.env['sica.shooting'].sudo().search([('member_id', '=', member.id)])
            if update_shooing_ids:
                for shooting in update_shooing_ids:
                    shooting_vals = {
                        'date': shooting.date.strftime("%Y-%m-%d") if shooting.date else '',
                        'mobile_number': shooting.mobile_number or '',
                        'shooting_title_id': shooting.shooting_title_id.id or False,
                        'member_name': shooting.member_name or '',
                        'member_number': shooting.member_number or '',
                        'grade': shooting.grade or '',
                        'dop_name': shooting.dop_name or '',
                        'dop_number': shooting.dop_number or '',
                        'dop_member_id': shooting.dop_member_id.id or False,
                        'designation': shooting.designation or '',
                        'project_title': shooting.project_title or '',
                        'medium': shooting.medium or '',
                        'medium_id': shooting.medium_id.id or False,
                        'producer': shooting.producer or '',
                        'production_house': shooting.production_house or '',
                        'production_executive': shooting.production_executive or '',
                        'production_executive_contact_no': shooting.production_executive_contact_no or '',
                        'location': shooting.location,
                        'outdoor_unit_name': shooting.outdoor_unit_name or '',
                        'notes': shooting.notes or '',
                        'state': shooting.state or '',
                        'update_shooing_id': shooting.id,
                    }
                    member_shooting.append(shooting_vals)

        return json.dumps({'Member Shooting': member_shooting})

    @http.route('/gat/dop/pending/shooting_approval', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_dop_pending_shooting_approval(self, **kw):

        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('DOP_MEMBERSHIP_ID')  # Corrected case for 'membership_id'

        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})

        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        member_shooting = []
        if membership_id:
            member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
            update_shooing_ids = request.env['sica.shooting'].sudo().search([('dop_member_id', '=', member.id), ('state', '=', 'Waiting For Dop Approval')])
            if update_shooing_ids:
                for shooting in update_shooing_ids:
                    shooting_vals = {
                        'date': shooting.date.strftime("%Y-%m-%d") if shooting.date else '',
                        'mobile_number': shooting.mobile_number or '',
                        'shooting_title_id': shooting.shooting_title_id.id or False,
                        'member_name': shooting.member_name or '',
                        'member_number': shooting.member_number or '',
                        'grade': shooting.grade or '',
                        'dop_name': shooting.dop_name or '',
                        'dop_number': shooting.dop_number or '',
                        'dop_member_id': shooting.dop_member_id.id or False,
                        'designation': shooting.designation or '',
                        'project_title': shooting.project_title or '',
                        'medium': shooting.medium or '',
                        'medium_id': shooting.medium_id.id or False,
                        'producer': shooting.producer or '',
                        'production_house': shooting.production_house or '',
                        'production_executive': shooting.production_executive or '',
                        'production_executive_contact_no': shooting.production_executive_contact_no or '',
                        'location': shooting.location,
                        'outdoor_unit_name': shooting.outdoor_unit_name or '',
                        'notes': shooting.notes or '',
                        'state': shooting.state or '',
                        'update_shooing_id': shooting.id,
                    }
                    member_shooting.append(shooting_vals)

        return json.dumps({'Member Shooting Pending Dop Approval': member_shooting})

    @http.route('/post/approve/dop/shooting', type='http', auth='none', methods=['POST'], csrf=False)
    def action_post_approve_dop_shooting(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        dop_membership_id = kw.get('DOP_MEMBERSHIP_ID')  # Corrected case for 'membership_id'
        update_shooting_id = kw.get('update_shooting_id')  # Corrected case for 'membership_id'
        status_move = kw.get('status_move')
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        if not dop_membership_id:
            return json.dumps({"error": "Membership ID is missing"})

        if dop_membership_id and update_shooting_id:
            dop_member = request.env['res.member'].sudo().search([('membership_no', '=', dop_membership_id)], limit=1)
            update_shooting = request.env['sica.shooting'].sudo().search([('id', '=', int(update_shooting_id)), ('dop_member_id', '=', dop_member.id)], limit=1)
            if update_shooting:
                if status_move == 'approve':
                    update_shooting.sudo().write({'state': "Dop Approved"})
                    return json.dumps({'Member Shooting Status': "Updated"})
                else:
                    update_shooting.sudo().write({'state': "Reject"})
                    return json.dumps({'Member Shooting Status': "Updated"})
            else:
                return json.dumps({"Missing Required": "DOp Member Number or Update Shooting ID"})

        return json.dumps({"Missing Required": "DOp Member Number or Update Shooting ID"})

    @http.route('/create/shooting_dop', type='http', auth='none', methods=['POST'], csrf=False)
    def action_create_shooting_dop(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')  # Corrected case for 'membership_id'

        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})

        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        data = kw.get('data')
        data = data.replace("'", '"')
        data_dict = json.loads(data)
        date = data_dict.get('date') or ''
        member_name = data_dict.get('member_name') or ''
        member_number = data_dict.get('member_number') or ''
        mobile_number = data_dict.get('mobile_number') or ''
        grade = data_dict.get('grade') or ''
        project_title = data_dict.get('project_title') or ''
        medium = data_dict.get('format_id') or ''
        schedule_start = data_dict.get('schedule_start') or ''
        schedule_end = data_dict.get('schedule_end') or ''
        producer = data_dict.get('producer') or ''
        production_house = data_dict.get('production_house') or ''
        production_executive = data_dict.get('production_executive') or ''
        production_executive_contact_no = data_dict.get('production_executive_contact_no') or ''
        location = data_dict.get('location') or ''
        outdoor_link_details = data_dict.get('outdoor_link_details') or ''
        associate_ids = data_dict.get('associate')
        shooting_title_id = request.env['shooting.title'].sudo().search([('name', '=', project_title)], limit=1)
        medium_id = request.env['member.medium'].sudo().search([('id', '=', int(medium))], limit=1)

        if membership_id == '':
            return json.dumps({"error": "Membership ID is mismatched"})
        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        sica_shooting_dop = request.env['shooting.dop'].sudo().create({
            'mobile_number': mobile_number,
            'member_id': member.id,
            'member_name': member_name,
            'member_number': member_number,
            'grade': grade,
            'medium_id': medium_id.id,
            'medium': medium_id.name,
            'schedule_start': datetime.strptime(schedule_start, "%d/%m/%Y").date(),
            'schedule_end': datetime.strptime(schedule_end, "%d/%m/%Y").date(),
            'date': datetime.strptime(date, "%d/%m/%Y").date(),
            'shooting_title_id': shooting_title_id.id or False,
            'project_title': project_title or '',
            'outdoor_link_details': outdoor_link_details or '',
            'producer': producer or '',
            'production_house': production_house or '',
            'production_executive': production_executive or '',
            'production_executive_contact_no': production_executive_contact_no or '',
            'location': location or '',
        })
        for associate in associate_ids:
            name = associate.get('name') or ''
            mobile_number = associate.get('mobile_number') or ''
            member_number = associate.get('member_number') or ''
            role_type = associate.get('role_type') or ''
            member = request.env['res.member'].sudo().search([('membership_no', '=', member_number)], limit=1)

            if member:
                create_associate = request.env['shooting.associate'].sudo().create({
                    'name': name,
                    'mobile_number': mobile_number,
                    'shooting_id': sica_shooting_dop.id or False,
                    'member_number': member_number or '',
                    'member_id': member.id or False,
                    'member_role_tpe': role_type or ''
                })
                # sica_shooting = request.env['sica.shooting'].sudo().create({
                #     'mobile_number': mobile_number,
                #     'member_id': member.id,
                #     'shooting_title_id': shooting_title_id.id,
                #     'member_name': member.name or '',
                #     'member_number': member_number,
                #     'designation': role_type or '',
                #     'medium_id': medium_id,
                #     'start_date': datetime.strptime(start_date, "%d/%m/%Y").date(),
                #     'end_date': datetime.strptime(end_date, "%d/%m/%Y").date(),
                # })

        return json.dumps({'Sica Shooting': 'Shooting DOP Created', 'ID': sica_shooting_dop.id})

    @http.route('/get/member/shooting_dop', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_member_shooting_dop(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')  # Corrected case for 'membership_id'

        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})

        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        if membership_id == '':
            return json.dumps({"error": "Membership ID is mismatched"})
        shooting_dop_details = []
        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        if member:
            shooting_dop_ids = request.env['shooting.dop'].sudo().search([('member_id', '=', member.id)])
            for shooting_dop in shooting_dop_ids:
                dop_vals = {
                    'mobile_number': shooting_dop.mobile_number or '',
                    'member_id': shooting_dop.member_id.id or False,
                    'member_name': shooting_dop.member_name or '',
                    'member_number': shooting_dop.member_number or '',
                    'grade': shooting_dop.grade or '',
                    'format_id': shooting_dop.medium_id.id or False,
                    'format_name': shooting_dop.medium_id.name or False,
                    'medium_id': shooting_dop.medium_id.id or False,
                    'medium': shooting_dop.medium or '',
                    'schedule_start': shooting_dop.schedule_start.strftime("%Y-%m-%d") if shooting_dop.schedule_start else '',
                    'schedule_end': shooting_dop.schedule_end.strftime("%Y-%m-%d") if shooting_dop.schedule_end else '',
                    'date': shooting_dop.date.strftime("%Y-%m-%d") if shooting_dop.date else '',
                    'shooting_title_id': shooting_dop.shooting_title_id.id or False,
                    'project_title': shooting_dop.project_title or '',
                    'producer': shooting_dop.producer or '',
                    'production_house': shooting_dop.production_house or '',
                    'production_executive': shooting_dop.production_executive or '',
                    'production_executive_contact_no': shooting_dop.production_executive_contact_no or '',
                    'location': shooting_dop.location,
                    'outdoor_link_details': shooting_dop.outdoor_link_details or '',
                }
                associate_vals = []
                for associate in shooting_dop.associate_ids:
                    associate_vals = {
                        'name': associate.name or '',
                        'mobile_number': associate.mobile_number or '',
                        'shooting_id': associate.shooting_id.id or False,
                        'member_number': associate.member_number or '',
                        'member_id': associate.member_id.id or False,
                        'member_role_tpe': associate.member_role_tpe or ''
                    }
                shooting_dop_details.append({'Shooting_dop': dop_vals, 'Added Members': associate_vals})
        return json.dumps({'Shooting DOP Details': shooting_dop_details})

    @http.route('/get/title/shooting_details', type='http', auth='none', methods=['GET'], csrf=False)
    def get_all_shooting_details(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        shooting_title = kw.get('shooting_title')
        shooting_details = []
        shooting_title_id = request.env['shooting.title'].sudo().search([('name', '=', shooting_title)], limit=1)
        if not shooting_title_id:
            return json.dumps({'shooting_all_details': shooting_details, "title": shooting_title})
        shooting_ids = request.env['sica.shooting'].sudo().search([('shooting_title_id', '=', shooting_title_id.id)])
        for shooting_dop in shooting_ids:
            shooting_vals = {
                'mobile_number': shooting_dop.mobile_number,
                'member_id': shooting_dop.member_id.id,
                'shooting_id': shooting_dop.id,
                'member_name': shooting_dop.member_name,
                'member_number': shooting_dop.member_number,
                'designation': shooting_dop.designation,
                'project_title': shooting_dop.project_title,
                'format_id': shooting_dop.medium_id.id,
                'format_name': shooting_dop.medium_id.name,
                'medium_id': shooting_dop.medium_id.id,
                'medium_name': shooting_dop.medium_id.name,
                'start_date': shooting_dop.start_date.strftime("%Y-%m-%d") if shooting_dop.start_date else '',
                'end_date': shooting_dop.end_date.strftime("%Y-%m-%d") if shooting_dop.end_date else '',
                'notes': shooting_dop.notes,
            }

            shooting_details.append({'shooting_details': shooting_vals})
        return json.dumps({'shooting_all_details': shooting_details, "title": shooting_title})


    @http.route('/get/all/shooting_dop_details', type='http', auth='none', methods=['GET'], csrf=False)
    def get_all_shooting_dop_details(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        shooting_dop_ids = request.env['shooting.dop'].sudo().search([])
        shooting_dop_details = []
        for shooting_dop in shooting_dop_ids:
            shooting_dop_vals = {
                'mobile_number': shooting_dop.mobile_number,
                'member_id': shooting_dop.member_id.id,
                'shooting_id': shooting_dop.id,
                'member_name': shooting_dop.member_name,
                'member_number': shooting_dop.member_number,
                'designation': shooting_dop.designation,
                'project_title': shooting_dop.project_title,
                'format_id': shooting_dop.medium_id.id,
                'format_name': shooting_dop.medium_id.name,
                'medium_id': shooting_dop.medium_id.id,
                'medium_name': shooting_dop.medium_id.name,
                'start_date': shooting_dop.start_date.strftime("%Y-%m-%d") if shooting_dop.start_date else '',
                'end_date': shooting_dop.end_date.strftime("%Y-%m-%d") if shooting_dop.end_date else '',
                'outdoor_link_details': shooting_dop.outdoor_link_details,
            }
            associate_vals = []
            for associate in shooting_dop.associate_ids:
                associate_vals.append({
                    'name': associate.name,
                    'mobile_number': associate.mobile_number,
                    'shooting_id': associate.shooting_id.id,
                    'member_number': associate.member_number,
                    'member_id': associate.member_id.id,
                    'associate_id': associate.id,
                })
            shooting_details = []
            if shooting_dop.shooting_id:
                shooting_details.append({
                    'mobile_number': shooting_dop.shooting_id.mobile_number,
                    'member_id': shooting_dop.shooting_id.member_id.id,
                    'shooting_id': shooting_dop.shooting_id.id,
                    'member_name': shooting_dop.shooting_id.member_name,
                    'member_number': shooting_dop.shooting_id.member_number,
                    'designation': shooting_dop.shooting_id.designation,
                    'project_title': shooting_dop.shooting_id.project_title,
                    'medium_id': shooting_dop.shooting_id.medium_id.id,
                    'medium_name': shooting_dop.shooting_id.medium_id.name,
                    'start_date': shooting_dop.shooting_id.start_date.strftime(
                        "%Y-%m-%d") if shooting_dop.start_date else '',
                    'end_date': shooting_dop.shooting_id.end_date.strftime("%Y-%m-%d") if shooting_dop.end_date else '',
                    'notes': shooting_dop.shooting_id.notes,
                    'id': shooting_dop.shooting_id.id,
                })

            shooting_dop_details.append({'shooting_dop_details': shooting_dop_vals, 'associate': associate_vals,
                                         'shooting_details': shooting_details})
        return json.dumps({'shooting_dop_all_details': shooting_dop_details})


    @http.route('/get/all/shooting_dop_approval', type='http', auth='none', methods=['GET'], csrf=False)
    def get_all_shooting_dop_approval(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        shooting_dop_ids = request.env['shooting.dop'].sudo().search([('end_date', '>', fields.Date.today())])
        dop_associate_details = []
        for shooting_dop in shooting_dop_ids:
            if shooting_dop.shooting_id.choose_dop_for_approval == 'YES':
                shooting_dop_vals = {
                    'mobile_number': shooting_dop.mobile_number,
                    'member_id': shooting_dop.member_id.id,
                    'shooting_id': shooting_dop.shooting_id.id,
                    'shooting_dop_id': shooting_dop.id,
                    'shooting_note': shooting_dop.shooting_id.notes,
                    'member_name': shooting_dop.member_id.name,
                    'member_number': shooting_dop.member_number,
                    'designation': shooting_dop.designation,
                    'project_title': shooting_dop.project_title,
                    'medium_id': shooting_dop.medium_id.id,
                    'medium_name': shooting_dop.medium_id.name,
                    'start_date': shooting_dop.start_date.strftime("%Y-%m-%d") if shooting_dop.start_date else '',
                    'end_date': shooting_dop.end_date.strftime("%Y-%m-%d") if shooting_dop.end_date else '',
                    'outdoor_link_details': shooting_dop.outdoor_link_details,
                    'attending': shooting_dop.attending,
                }
                associate_vals = []
                for associate in shooting_dop.associate_ids:
                    associate_vals.append({
                        'associate_id': associate.id,
                        'mobile_number': associate.mobile_number,
                        'shooting_id': associate.shooting_id.id,
                        'member_number': associate.member_number,
                        'member_id': associate.member_id.id,
                        'shooting_note': shooting_dop.shooting_id.notes,
                        'member_name': associate.member_id.name,
                        'designation': associate.member_id.designation,
                        'project_title': associate.shooting_id.project_title,
                        'medium_id': associate.shooting_id.medium_id.id,
                        'medium_name': associate.shooting_id.medium_id.name,
                        'start_date': associate.shooting_id.start_date.strftime(
                            "%Y-%m-%d") if associate.shooting_id.start_date else '',
                        'end_date': associate.shooting_id.end_date.strftime(
                            "%Y-%m-%d") if associate.shooting_id.end_date else '',
                        'outdoor_link_details': associate.shooting_id.outdoor_link_details,
                        'attending': associate.attending,
                    })

                    shooting_details = []
                    if shooting_dop.shooting_id:
                        shooting_details.append({
                            'mobile_number': shooting_dop.shooting_id.mobile_number,
                            'member_id': shooting_dop.shooting_id.member_id.id,
                            'shooting_id': shooting_dop.shooting_id.id,
                            'member_name': shooting_dop.shooting_id.member_name,
                            'member_number': shooting_dop.shooting_id.member_number,
                            'designation': shooting_dop.shooting_id.designation,
                            'project_title': shooting_dop.shooting_id.project_title,
                            'medium_id': shooting_dop.shooting_id.medium_id.id,
                            'medium_name': shooting_dop.shooting_id.medium_id.name,
                            'start_date': shooting_dop.shooting_id.start_date.strftime(
                                "%Y-%m-%d") if shooting_dop.start_date else '',
                            'end_date': shooting_dop.shooting_id.end_date.strftime(
                                "%Y-%m-%d") if shooting_dop.end_date else '',
                            'notes': shooting_dop.shooting_id.notes,
                            'id': shooting_dop.shooting_id.id,
                        })
                dop_associate_details.append({'shooting_dop_details': shooting_dop_vals, 'associate': associate_vals,
                                              'shooting_details': shooting_details})
        return json.dumps({'dop_associate_all_details': dop_associate_details})


    @http.route('/create/shooting_associate', type='http', auth='none', methods=['POST'], csrf=False)
    def action_create_shooting_associate(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')
        shooting_id = kw.get('shooting_id')
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        data = kw.get('data')
        data = data.replace("'", '"')
        data_dict = json.loads(data)
        name = data_dict.get('name')
        mobile_number = data_dict.get('mobile_number')
        member_number = data_dict.get('member_number')
        role_type = data_dict.get('role_type')

        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        if member:
            create_works = request.env['shooting.associate'].sudo().create({
                'name': name,
                'mobile_number': mobile_number,
                'shooting_id': shooting_id,
                'member_number': member_number,
                'member_id': member.id,
                'role_type': role_type
            })
            return json.dumps({'Associate': 'associate_created', 'ID': create_works.id})
        else:
            return json.dumps({"error": "Membership ID is mismatched"})


    @http.route('/update/shooting_associate', type='http', auth='none', methods=['POST'], csrf=False)
    def action_update_shooting_associate(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')
        associate_id = kw.get('Associate_id')
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        data = kw.get('data')
        data = data.replace("'", '"')
        data_dict = json.loads(data)
        name = data_dict.get('name')
        mobile_number = data_dict.get('mobile_number')
        member_number = data_dict.get('member_number')
        associate_id = request.env['shooting.associate'].sudo().search([('id', '=', associate_id)], limit=1)

        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        if member:
            associate_id.sudo().write({
                'name': name,
                'mobile_number': mobile_number,
                'member_id': member.id,
                'member_number': member_number,

            })
            return json.dumps({'Associate': 'associate_updated', 'ID': associate_id.id})
        else:
            return json.dumps({"error": "Membership ID is mismatched"})


    @http.route('/update/dop_associate_attending', type='http', auth='none', methods=['POST'], csrf=False)
    def action_update_dop_associate_attending(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        membership_id = kw.get('MEMBERSHIP_ID')
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        if not membership_id:
            return json.dumps({"error": "Membership ID is missing"})
        data = kw.get('data')
        data = data.replace("'", '"')
        data_dict = json.loads(data)
        shooting_dop_id = data_dict.get('shooting_dop_id')
        associate_id = data_dict.get('associate_id')
        attending = data_dict.get('attending')
        reason = data_dict.get('reason')
        if attending == 'True':
            attending = True
        else:
            attending = False

        member = request.env['res.member'].sudo().search([('membership_no', '=', membership_id)], limit=1)
        if member:
            if shooting_dop_id:
                shooting_dop_id = request.env['shooting.dop'].sudo().search([('id', '=', shooting_dop_id)])
                shooting_dop_id.sudo().write({
                    'attending': attending,
                })
                return json.dumps({'Shooting Dop Updated': shooting_dop_id.id})
            associate_id = request.env['shooting.associate'].sudo().search([('id', '=', associate_id)])
            if associate_id:
                associate_id.sudo().write({
                    'attending': attending,
                    'not_attending_reason': reason,
                })
                return json.dumps({'Shooting Dop Updated': associate_id.id})
        else:
            return json.dumps({"error": "Membership ID is mismatched"})
