# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _


class ProfitLoss(models.Model):
    _name = "profit.loss"
    _description = "Profit & Loss Entries"
    _order = "transaction_date asc, transaction_type desc, id asc"

    sica_cbt = fields.Selection([
        ("SICA", "SICA"),
        ("CBT", "CBT"),
    ], string="SICA/CBT")
    transaction_date = fields.Date(required=True, string="Transaction Date")
    transaction_type = fields.Selection([
        ("Income", "Income"),
        ("Expense", "Expense"),
    ], required=True, string="Transaction Type")
    description = fields.Char(required=True, string="Description")
    cash = fields.Float(string="Cash")
    bank = fields.Float(string="Bank")
    res_model = fields.Char(required=True, readonly=True)
    res_id = fields.Integer(required=True, readonly=True)


ProfitLoss()
