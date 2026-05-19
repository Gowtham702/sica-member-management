# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError

class ExpenseType(models.Model):
    _name = "expense.type"
    _description = 'Expense Type'
    name = fields.Char()


class Expense(models.Model):
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _name = "member.expense"
    _description = "Expense Management"
    _rec_name = "voucher_no"
    _order = "id desc"

    state = fields.Selection([
        ("draft", "Draft"),
        ("validated", "Validated"),
    ], default="draft", copy=False, tracking=True, string="Status")
    name = fields.Char(tracking=True, states={'validated': [('readonly', True)]}, string="To")
    voucher_no = fields.Char(default="/", required=True, tracking=True, string="Voucher No.")
    voucher_date = fields.Date(required=True, tracking=True, states={'validated': [('readonly', True)]}, string="Voucher Date")
    expense_type_id = fields.Many2one('expense.type', string="Section")
    expense_type = fields.Selection([
        ("salaries", "Salaries"),
        ("food_expenses", "Food Expenses"),
        ("professional_fees", "Professional Fees"),
        ("local_conveyance_fuel", "Local Conveyance and Fuel"),
        ("tea_coffee_snacks", "Tea, Coffee and Snacks Expenses"),
        ('agm_expense', 'AGM Exp'),
        ('broadband_expenses', 'Broadband Expenses'),
        ('cbt_to_sica', 'CBT to SICA'),
        ('SICA to CBT', 'SICA to CBT'),
        ('dispute_amount_settlement', 'Dispute Amount Settlement'),
        ('donation_given', 'Donations given'),
        ('education_loan', 'Education Loan'),
        ('Electricity Expenses', 'Electricity Expenses'),
        ('FEFSI', 'FEFSI'),
        ('Hand loan', 'Hand loan'),
        ('IT Expenses ', 'IT Expenses'),
        ('LCF Settelement', 'LCF Settelement'),
        ('LCF Part payment', 'LCF Part payment'),
        ('Loan', 'Loan'),
        ('Misc Expenses', 'Misc Expenses'),
        ('News Paper Exp', 'News Paper Exp'),
        ('Marriage Gift', 'Marriage Gift'),
        ('Office Repairs & Maintenance', 'Office Repairs & Maintenance'),
        ('Pension to Members', 'Pension to Members'),
        ('Other Union Donation', 'Other Union Donation'),
        ('Pension to Members', 'Pension to Members'),
        ('Petrol Expenses', 'Petrol Expenses'),
        ('Pooja Exp', 'Pooja Exp'),
        ('Petrol Expenses', 'Petrol Expenses'),
        ('Postage & Courier ', 'Postage & Courier'),
        ('Prasad Lab Theatre', 'Prasad Lab Theatre'),
        ('Printing', 'Printing'),
        ('Rent Expenses', 'Rent Expenses'),
        ('Stationary', 'Stationary'),
        ('Water can  Exp', 'Water can  Exp'),
        ('xerox', 'xerox'),
        ('Training Expenses', 'Training Expenses'),
        ('Telephone Expenses ', 'Telephone Expenses'),
        ('Travel Expenses', 'Travel Expenses'),
        ('xerox', 'xerox')
    ], tracking=True, states={'validated': [('readonly', True)]}, string="Expense Type")
    sica_cbt = fields.Selection([
        ("sica", "SICA"),
        ("cbt", "CBT"),
    ], tracking=True, required=True, states={'validated': [('readonly', True)]}, string="SICA/CBT")
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    amount = fields.Monetary(currency_field="currency_id", required=True, tracking=True, states={'validated': [('readonly', True)]}, string="Amount")
    amount_in_words = fields.Text(string="Amount (In words)", required=True, states={'validated': [('readonly', True)]}, tracking=True)
    expense_reason = fields.Char(string="For", tracking=True, states={'validated': [('readonly', True)]})
    payment_option = fields.Selection([
        ("cash", "Cash"),
        ("dd", "DD"),
        ("cheque", "CHEQUE"),
        ("online_transfer", "ONLINE TRANSFER"),
        ("edc_machine", "EDC MACHINE"),
        ("sica_app", "SICA APP"),
    ], tracking=True, states={'validated': [('readonly', True)]}, string="Payment Option")
    reference_no = fields.Char(string="Reference No.", states={'validated': [('readonly', True)]})
    edit_reason = fields.Date(string="Edit Reason", tracking=True, states={'validated': [('readonly', True)]})

    @api.onchange('amount')
    def onchange_amount(self):
        self.amount_in_words = self.currency_id.amount_to_text(self.amount)
    
    @api.onchange('expense_type_id')
    def _onchange_expense_type_id(self):
        if self.expense_type_id:
            # Example: autofill or modify behavior
            self.expense_reason = f"{self.expense_type_id.name}"

    # @api.onchange('expense_type_id')
    # def _onchange_expense_type_id(self):
    #     if self.expense_type_id and not self.expense_reason:
    #         return {
    #             'warning': {
    #                 'title': "Missing Reason",
    #                 'message': "Please enter a reason for the selected expense type."
    #             }
    #         }


    def button_validate(self):
        self.ensure_one()
        if self.state == "validated":
            return False
        vals = {"state": "validated"}
        if self.voucher_no == "/":
            vals.update({"voucher_no": self.env["ir.sequence"].next_by_code("member.expense")})
        pl_vals = {}
        pl_vals["sica_cbt"] = self.sica_cbt.upper()
        pl_vals["transaction_date"] = self.voucher_date
        pl_vals["transaction_type"] = "Expense"
        pl_vals["description"] = self.expense_type_id.id
        pl_vals["cash"] = -self.amount
        pl_vals["res_model"] = "member.expense"
        pl_vals["res_id"] = self.id
        self.env["profit.loss"].create(pl_vals)
        return self.write(vals)

    def unlink(self):
        for expense in self:
            if expense.state == "validated":
                raise UserError("Not allowed to delete the validated expense voucher")
        return super(Expense, self).unlink()

Expense()