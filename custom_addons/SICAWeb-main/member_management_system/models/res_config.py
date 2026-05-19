from odoo import models, fields, api, _
from num2words import num2words


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    under_maintenance = fields.Boolean(string='Under Maintenance', config_parameter='member_management_system.under_maintenance')
    app_update = fields.Char(string='App Update', config_parameter='member_management_system.app_update', default='1.0.0')
    penalty_fee = fields.Float(config_parameter='member_management_system.penalty_fee', default='0.0')
    payment_gateway_notes = fields.Char(config_parameter='member_management_system.payment_gateway_notes', default='Amount in INR')