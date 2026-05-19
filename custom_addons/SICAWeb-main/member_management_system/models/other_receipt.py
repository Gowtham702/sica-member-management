# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError

class OtherReceipt(models.Model):
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _name = "other.receipt"
    _description = "Other Receipts"
    _rec_name = "receipt_no"
    _order = "id desc"

    state = fields.Selection([
        ("draft", "Draft"),
        ("validated", "Validated"),
    ], default="draft", copy=False, tracking=True, string="Status")
    name = fields.Char(required=True, tracking=True, states={'validated': [('readonly', True)]}, string="Received From")
    pan = fields.Char(required=False, tracking=True, states={'validated': [('readonly', True)]}, string="Pan Number")
    receipt_no = fields.Char(default="/", readonly=True, required=True, tracking=True, string="Receipt No.")
    receipt_date = fields.Date(required=True, tracking=True, states={'validated': [('readonly', True)]}, string="Receipt Date")
    company_id = fields.Many2one('res.company', required=True, readonly=True, states={'validated': [('readonly', True)]}, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    amount = fields.Monetary(currency_field="currency_id", required=True, tracking=True, states={'validated': [('readonly', True)]}, string="Amount")
    amount_in_words = fields.Text(string="Amount (In words)", required=True, tracking=True, states={'validated': [('readonly', True)]})
    payment_option = fields.Selection([
        ("cash", "Cash"),
        ("dd", "DD"),
        ("cheque", "CHEQUE"),
        ("online_transfer", "ONLINE TRANSFER"),
        ("edc_machine", "EDC MACHINE"),
        ("sica_app", "SICA APP"),
    ], tracking=True, required=True, states={'validated': [('readonly', True)]}, string="Payment Option")
    payment_date = fields.Date(string="Payment Date", required=True, tracking=True, states={'validated': [('readonly', True)]})
    receipt_type = fields.Selection([
        ("application_form", "Application Form"),
        ("donation", "Donation"),
        ("dispute", "Dispute"),
        ("sica_to_cbt", "SICA to CBT"),
        ("cbt_to_sica", "CBT to SICA"),
        ("vendor", "Vendor"),
    ], tracking=True, required=True, states={'validated': [('readonly', True)]}, string="Receipt Type")
    donation_type = fields.Char(string="Donation Type")
    payment_ref = fields.Char(string="Payment Reference", states={'validated': [('readonly', True)]})
    vendor_ref = fields.Char(string="Vendor Reference", states={'validated': [('readonly', True)]})

    @api.onchange('amount')
    def onchange_amount(self):
        self.amount_in_words = self.currency_id.amount_to_text(self.amount)

    @api.onchange('receipt_type')
    def receipt_type_onchange(self):
        if self.receipt_type != 'donation':
            self.donation_type = False

    def button_validate(self):
        self.ensure_one()
        if self.state == "validated":
            return False
        vals = {"state": "validated"}
        if self.receipt_no == "/":
            vals.update({"receipt_no": self.env["ir.sequence"].next_by_code("other.receipt")})
        pl_vals = {}
        pl_vals["transaction_date"] = self.payment_date
        pl_vals["transaction_type"] = "Income"
        pl_vals["description"] = dict(self._fields['receipt_type'].selection).get(self.receipt_type)
        pl_vals["cash"] = self.amount if self.payment_option == "cash" else 0
        pl_vals["bank"] = self.amount if self.payment_option != "cash" else 0
        pl_vals["res_model"] = "other.receipt"
        pl_vals["res_id"] = self.id
        self.env["profit.loss"].create(pl_vals)
        return self.write(vals)

    def unlink(self):
        for receipt in self:
            if receipt.state == "validated":
                raise UserError("Not allowed to delete the validated receipt")
        return super(OtherReceipt, self).unlink()

OtherReceipt()
