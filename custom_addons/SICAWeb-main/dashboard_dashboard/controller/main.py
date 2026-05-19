import json
from odoo.tools.translate import _
from odoo import http
from odoo.http import content_disposition, request, serialize_exception
from odoo.tools import html_escape
import requests
from datetime import datetime
import base64

class PrivacyPolicy(http.Controller):

	@http.route(['/privacypolicy'], type='http', auth="public", website=True)
	def privacy_policy(self):
		vals = {}
		policy = request.env['privacy.policy'].sudo().search([('is_publish','=',True)], limit=1)
		vals.update({
			'policy': policy,
			})
		return request.render("dashboard_dashboard.privacy_policy", vals)


