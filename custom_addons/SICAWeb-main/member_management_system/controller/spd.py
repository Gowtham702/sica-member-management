from odoo import http, fields
from odoo.http import request
import json
import random
import requests
import datetime
from datetime import datetime
import razorpay

class MemberDiscussion(http.Controller):
    @http.route('/get/spd/category', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_spd_category(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        event_category_ids = request.env['spd.category'].sudo().search([])
        category_details = []
        for category in event_category_ids:
            category_details.append({
                'category_name': category.name or '',
                'description': category.description or '',
                'category_id': category.id
            })
        return json.dumps({'spd_category_details': category_details})

    @http.route('/get/spd/sub/category', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_sub_spd_category(self, **kw):
        api_key = kw.get('api_key')
        category_id = kw.get('category_id')

        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"

        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})

        # if not category_id:
        #     return json.dumps({"error": "category_id is missing"})

        sub_category_ids = request.env['spd.sub.category'].sudo().search([])
        category_details = []

        for sub_category in sub_category_ids:
            # build product list for this subcategory
            product_list = []
            for product in sub_category.product_ids:
                product_list.append({
                    'id': product.id,
                    'name': product.name or '',
                    'sequence': product.sequence or 0,
                    'description': product.description or '',
                    'quantity': product.quantity or 0,
                    'category_id': product.category_id.id if product.category_id else False,
                    'category_name': product.category_id.name if product.category_id else '',
                    'image_link': product.image_link or '',
                      # optional base64
                })

            category_details.append({
                'vendor_name': sub_category.name or '',
                'company_name': sub_category.company_name or '',
                'vendor_type': sub_category.vendor_type or '',
                'phone_number': sub_category.phone_number or '',
                'email': sub_category.email or '',
                'website': sub_category.website or '',
                'address': sub_category.address or '',
                # 'sub_category_id': sub_category.id,
                'location': sub_category.location or '',
                'image': sub_category.photo.decode('utf-8') if sub_category.photo else '',
                'active': sub_category.active or '',
                'state': sub_category.state or '',
                'products': product_list,  # ✅ Include product_ids here
            })

        return json.dumps({'spd_category_details': category_details})

    @http.route('/get/spd/sub/category/product', type='http', auth='none', methods=['GET'], csrf=False)
    def action_get_spd_product(self, **kw):
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        sub_category_id = kw.get('sub_category_id')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url.image')
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        sub_category = request.env['spd.sub.category'].sudo().search([('id', '=', int(sub_category_id))])
        product_ids = request.env['product.vendor'].sudo().search([('vendor_id', '=', int(sub_category_id))])
        product_details = []
        for product_id in product_ids:
            image = base_url + '/web/image?' + 'model=spd.sub.category&id=' + str(sub_category.id) + '&field=photo'
            product_details.append({
                'product_name': product_id.product_id.name or '',
                'description': product_id.product_id.description or '',
                'vendor_logo_image': image
            })
        return json.dumps({'product_details': product_details})

    @http.route('/get/spd/banner', type='http', auth='none', methods=['GET'], csrf=False)
    def get_spd_banner(self, **kw):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url.image')
        api_key = kw.get('api_key')  # Extract the API key from the GET parameters
        stored_api_key = "8f4f506e4b4022e154ac3651f9ee006e9b751261"
        if not api_key:
            return json.dumps({"error": "API key is missing"})
        if api_key != stored_api_key:
            return json.dumps({"error": "Invalid API key"})
        banner_list = []
        for spd_banner in request.env['spd.banner.photo'].sudo().search([('photo', '!=', False)]):
            vals = {}
            vals['sequence'] = spd_banner.sequence or ''
            vals['name'] = spd_banner.name or ''
            vals['image_url'] = base_url + '/web/image?' + 'model=spd.banner.photo&id=' + str(spd_banner.id) + '&field=photo' or ''
            vals['image'] = str(spd_banner.photo)
            vals['promotion_link'] = spd_banner.promotion_link or ''
            vals['description'] = spd_banner.description or ''
            vals['active'] = spd_banner.active or ''
            banner_list.append(vals)
        return json.dumps({'spd_banner': banner_list})
