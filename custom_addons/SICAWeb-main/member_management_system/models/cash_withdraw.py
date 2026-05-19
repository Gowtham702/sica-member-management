# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError


class CashWithdraw(models.Model):
    _name = "cash.withdraw"
    _description = "Cash Withdraw"
    _order = "id desc"
    _rec_name = "payment_option"

    state = fields.Selection([
        ("draft", "Draft"),
        ("validated", "Validated"),
    ], default="draft", copy=False, string="Status")
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    amount = fields.Monetary(currency_field="currency_id", required=True, states={'validated': [('readonly', True)]},
                             string="Withdraw Amount")
    amount_in_words = fields.Text(string="Amount (In words)", required=True, states={'validated': [('readonly', True)]})
    payment_option = fields.Selection([
        ("sica", "SICA"),
        ("cbt", "CBT"),
        ("other", "Other"),
    ], required=True, states={'validated': [('readonly', True)]}, string="Payment Option")
    payment_date = fields.Date(required=True, states={'validated': [('readonly', True)]}, string="Payment Date")

    @api.onchange('amount')
    def onchange_amount(self):
        self.amount_in_words = self.currency_id.amount_to_text(self.amount)

    def button_validate(self):
        self.ensure_one()
        if self.state == "validated":
            return False
        pl_vals = {}
        pl_vals["sica_cbt"] = self.payment_option.upper() if self.payment_option in ["sica", "cbt"] else False
        pl_vals["transaction_date"] = self.payment_date
        pl_vals["transaction_type"] = "Income"
        pl_vals["description"] = "Cash Deposit"
        pl_vals["cash"] = self.amount
        pl_vals["bank"] = -self.amount
        pl_vals["res_model"] = "cash.withdraw"
        pl_vals["res_id"] = self.id
        self.env["profit.loss"].create(pl_vals)
        return self.write({"state": "validated"})

    def unlink(self):
        for withdraw in self:
            if withdraw.state == "validated":
                raise UserError("Not allowed to delete the validated record")
        return super(CashWithdraw, self).unlink()


CashWithdraw()
