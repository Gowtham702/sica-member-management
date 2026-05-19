# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date


class SicaCbtReceipt(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = "sica.cbt.receipt"
    _description = "SICA/CBT Receipts"
    _rec_name = "display_name"
    _order = "id desc"

    @api.depends('subscription', 'mbf', 'fsf', 'aifec', 'uni_mei', 'mem_card_fee', 'sica_donation', 'admission',
                 'late_fee', 'sica_misc', 'sica_amount1', 'sica_amount2', 'dispute_amount')
    def _get_sica_total(self):
        for receipt in self:
            receipt.sica_total = receipt.subscription + receipt.mbf + receipt.fsf + receipt.aifec + receipt.uni_mei + receipt.mem_card_fee + receipt.sica_donation + receipt.admission + receipt.late_fee + receipt.sica_misc + receipt.sica_amount1 + receipt.sica_amount2 + receipt.dispute_amount

    @api.depends('cab_benefit_trust', 'life_coverage_fund', 'cbt_misc', 'cbt_donation', 'cbt_amount1', 'cbt_amount2',
                 'cbt_amount3')
    def _get_cbt_total(self):
        for receipt in self:
            receipt.cbt_total = receipt.cab_benefit_trust + receipt.life_coverage_fund + receipt.cbt_misc + receipt.cbt_donation + receipt.cbt_amount1 + receipt.cbt_amount2 + receipt.cbt_amount3

    @api.depends('sica_receipt_no', 'cbt_receipt_no')
    def _compute_display_name(self):
        for member in self:
            member.display_name = "%s/%s" % (member.sica_receipt_no, member.cbt_receipt_no)

    state = fields.Selection([
        ("draft", "Draft"),
        ("validated", "Validated"),
    ], default="draft", copy=False, tracking=True, string="Status")
    sica_receipt_no = fields.Char(default="/",  tracking=True, string="SICA Receipt No.")
    cbt_receipt_no = fields.Char(default="/",  tracking=True, string="CBT Receipt No.")
    display_name = fields.Char(compute='_compute_display_name', store=True, index=True)
    member_id = fields.Many2one("res.member",  tracking=True, string="Member",
                                states={'validated': [('readonly', True)]})
    membership_no = fields.Char(related="member_id.membership_no", readonly=True, string="Membership No.")
    member_name = fields.Char(related="member_id.name", readonly=True, string="Member's Name")
    receipt_date = fields.Date(tracking=True, states={'validated': [('readonly', True)]},
                               string="Receipt Date")

    # Personal Details
    grade = fields.Selection([
        ("life", "Life"),
        ("active", "Active"),
        ("associate", "Associate"),
        ("junior", "Junior")
    ], tracking=True, string="Grade", states={'validated': [('readonly', True)]})
    address = fields.Text(string="Address", tracking=True, states={'validated': [('readonly', True)]})
    contact_no = fields.Char(string="Contact No.", tracking=True, states={'validated': [('readonly', True)]})
    subscription_from = fields.Char(string="Subscription From", tracking=True,
                                    states={'validated': [('readonly', True)]})
    subscription_to = fields.Char(string="Subscription To", tracking=True, states={'validated': [('readonly', True)]})
    subscription_start = fields.Date(string="Subscription From", tracking=True)
    subscription_end = fields.Date(string="Subscription To", tracking=True)
    payment_option = fields.Selection([
        ("cash", "Cash"),
        ("dd", "DD"),
        ("cheque", "CHEQUE"),
        ("online_transfer", "ONLINE TRANSFER"),
        ("edc_machine", "EDC MACHINE"),
        ("sica_app", "SICA APP"),
    ], tracking=True,  string="Payment Option", states={'validated': [('readonly', True)]})
    payment_ref = fields.Char(string="Payment Reference", tracking=True, states={'validated': [('readonly', True)]})
    company_id = fields.Many2one('res.company', readonly=True, default=lambda self: self.env.company,
                                 states={'validated': [('readonly', True)]})
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id,
                                  states={'validated': [('readonly', True)]})

    # SICA Receipt
    subscription = fields.Monetary(currency_field="currency_id", tracking=True, string="Subscription",
                                   states={'validated': [('readonly', True)]})
    mbf = fields.Monetary(currency_field="currency_id", tracking=True, string="MBF",
                          states={'validated': [('readonly', True)]})
    fsf = fields.Monetary(currency_field="currency_id", tracking=True, string="FSF",
                          states={'validated': [('readonly', True)]})
    aifec = fields.Monetary(currency_field="currency_id", tracking=True, string="AIFEC",
                            states={'validated': [('readonly', True)]})
    uni_mei = fields.Monetary(currency_field="currency_id", tracking=True, string="UNI MEI",
                              states={'validated': [('readonly', True)]})
    mem_card_fee = fields.Monetary(currency_field="currency_id", tracking=True, string="Mem. Card Fee",
                                   states={'validated': [('readonly', True)]})
    sica_donation = fields.Monetary(currency_field="currency_id", tracking=True, string="SICA Donation",
                                    states={'validated': [('readonly', True)]})
    admission = fields.Monetary(currency_field="currency_id", tracking=True, string="Admission/Re-Admission",
                                states={'validated': [('readonly', True)]})
    late_fee = fields.Monetary(currency_field="currency_id", tracking=True, string="Late Fee",
                               states={'validated': [('readonly', True)]})
    sica_misc = fields.Monetary(currency_field="currency_id", tracking=True, string="SICA Miscellaneous",
                                states={'validated': [('readonly', True)]})
    sica_field1 = fields.Char(string="SICA Field1", tracking=True, states={'validated': [('readonly', True)]})
    sica_amount1 = fields.Monetary(string="SICA Amount1", currency_field="currency_id", tracking=True,
                                   states={'validated': [('readonly', True)]})
    sica_field2 = fields.Char(string="SICA Field2", tracking=True, states={'validated': [('readonly', True)]})
    sica_amount2 = fields.Monetary(string="SICA Amount2", currency_field="currency_id", tracking=True,
                                   states={'validated': [('readonly', True)]})
    dispute_amount = fields.Monetary(currency_field="currency_id", tracking=True, string="Dispute Amount",
                                     states={'validated': [('readonly', True)]})
    dispute_category = fields.Selection([
        ("film", "Film"),
        ("tv_serial", "TV Serial"),
    ], string="Dispute Category", tracking=True, states={'validated': [('readonly', True)]})
    sica_total = fields.Monetary(compute="_get_sica_total", currency_id="currency_id", store=True, string="Total Amount")
    sica_amount_in_words = fields.Text(string="Amount (In words)", tracking=True,
                                       states={'validated': [('readonly', True)]})

    # CBT Receipt
    cab_benefit_trust = fields.Monetary(currency_id="currency_id", tracking=True, string="CAM Benefit Trust",
                                        states={'validated': [('readonly', True)]})
    life_coverage_fund = fields.Monetary(currency_id="currency_id", tracking=True, string="Life Coverage Fund",
                                         states={'validated': [('readonly', True)]})
    cbt_misc = fields.Monetary(currency_id="currency_id", tracking=True, string="CBT Miscellaneous",
                               states={'validated': [('readonly', True)]})
    cbt_donation = fields.Monetary(currency_id="currency_id", tracking=True, string="CBT Donation",
                                   states={'validated': [('readonly', True)]})
    cbt_field1 = fields.Char(string="CBT Field1", default="Film Donation", tracking=True, states={'validated': [('readonly', True)]})
    cbt_amount1 = fields.Monetary(string="CBT Amount1", currency_id="currency_id", tracking=True,
                                  states={'validated': [('readonly', True)]})
    cbt_field2 = fields.Char(string="CBT Field2", tracking=True, states={'validated': [('readonly', True)]})
    cbt_amount2 = fields.Monetary(string="CBT Amount2", currency_id="currency_id", tracking=True,
                                  states={'validated': [('readonly', True)]})
    cbt_field3 = fields.Char(string="CBT Field3", tracking=True, states={'validated': [('readonly', True)]})
    cbt_amount3 = fields.Monetary(string="CBT Amount3", currency_id="currency_id", tracking=True,
                                  states={'validated': [('readonly', True)]})
    cbt_total = fields.Monetary(compute="_get_cbt_total", currency_id="currency_id", store=True, string="Total Amount")
    cbt_amount_in_words = fields.Text(string="Amount (In words)",  tracking=True,
                                      states={'validated': [('readonly', True)]})

    @api.onchange('member_id')
    def onchange_member(self):
        if self.member_id:
            member = self.member_id
            self.address = member.get_residential_address()
            if member.contact1 and member.contact2:
                self.contact_no = "%s/%s" % (member.contact1, member.contact2)
            else:
                self.contact_no = member.contact1 if member.contact1 else member.contact2
            self.grade = member.grade

    @api.onchange('subscription', 'mbf', 'fsf', 'aifec', 'uni_mei', 'mem_card_fee', 'sica_donation', 'admission',
                  'late_fee', 'sica_misc', 'sica_amount1', 'sica_amount2', 'dispute_amount')
    def onchange_sica_total(self):
        sica_total = self.subscription + self.mbf + self.fsf + self.aifec + self.uni_mei + self.mem_card_fee + self.sica_donation + self.admission + self.late_fee + self.sica_misc + self.sica_amount1 + self.sica_amount2 + self.dispute_amount
        self.sica_amount_in_words = self.currency_id.amount_to_text(sica_total)

    @api.onchange('cab_benefit_trust', 'life_coverage_fund', 'cbt_misc', 'cbt_donation', 'cbt_amount1', 'cbt_amount2',
                  'cbt_amount3')
    def onchange_cbt_total(self):
        cbt_total = self.cab_benefit_trust + self.life_coverage_fund + self.cbt_misc + self.cbt_donation + self.cbt_amount1 + self.cbt_amount2 + self.cbt_amount3
        self.cbt_amount_in_words = self.currency_id.amount_to_text(cbt_total)

    def button_validate(self):
        self.ensure_one()
        if self.state == "validated":
            return False
        if not self.sica_total and not self.cbt_total:
            raise UserError("Nothing to bill")
        vals = {"state": "validated"}
        if self.sica_receipt_no == "/" and self.sica_total:
            vals.update({"sica_receipt_no": self.env["ir.sequence"].next_by_code("sica.receipt")})
            self.env["sica.receipt"].create({"sica_cbt_id": self.id})
            pl_vals = {}
            pl_vals["sica_cbt"] = "SICA"
            pl_vals["transaction_date"] = self.receipt_date
            pl_vals["transaction_type"] = "Income"
            pl_vals["description"] = "SICA Receipt"
            pl_vals["cash"] = self.sica_total if self.payment_option == "cash" else 0
            pl_vals["bank"] = self.sica_total if self.payment_option != "cash" else 0
            pl_vals["res_model"] = "sica.receipt"
            pl_vals["res_id"] = self.id
            self.env["profit.loss"].create(pl_vals)
        if self.cbt_receipt_no == "/" and self.cbt_total:
            vals.update({"cbt_receipt_no": self.env["ir.sequence"].next_by_code("cbt.receipt")})
            self.env["cbt.receipt"].create({"sica_cbt_id": self.id})
            pl_vals = {}
            pl_vals["sica_cbt"] = "CBT"
            pl_vals["transaction_date"] = self.receipt_date
            pl_vals["transaction_type"] = "Income"
            pl_vals["description"] = "CBT Receipt"
            pl_vals["cash"] = self.cbt_total if self.payment_option == "cash" else 0
            pl_vals["bank"] = self.cbt_total if self.payment_option != "cash" else 0
            pl_vals["res_model"] = "cbt.receipt"
            pl_vals["res_id"] = self.id
            self.env["profit.loss"].create(pl_vals)
        if self.subscription_end:
            self.member_id.write({'subscription_end_date': self.subscription_end})
        return self.write(vals)

    def button_validate_new(self):
        if self.state == 'draft' and self.cbt_total or self.sica_total:
            self.ensure_one()
            if self.state == "validated":
                return False
            if not self.sica_total and not self.cbt_total:
                print(self.id, 'ID')
                raise UserError("Nothing to bill")

            vals = {"state": "validated"}
            if self.sica_total:
                self.env["sica.receipt"].create({"sica_cbt_id": self.id})
                pl_vals = {}
                pl_vals["sica_cbt"] = "SICA"
                pl_vals["transaction_date"] = self.receipt_date
                pl_vals["transaction_type"] = "Income"
                pl_vals["description"] = "SICA Receipt"
                pl_vals["cash"] = self.sica_total if self.payment_option == "cash" else 0
                pl_vals["bank"] = self.sica_total if self.payment_option != "cash" else 0
                pl_vals["res_model"] = "sica.receipt"
                pl_vals["res_id"] = self.id
                self.env["profit.loss"].create(pl_vals)
            if  self.cbt_total:
                self.env["cbt.receipt"].create({"sica_cbt_id": self.id})
                pl_vals = {}
                pl_vals["sica_cbt"] = "CBT"
                pl_vals["transaction_date"] = self.receipt_date
                pl_vals["transaction_type"] = "Income"
                pl_vals["description"] = "CBT Receipt"
                pl_vals["cash"] = self.cbt_total if self.payment_option == "cash" else 0
                pl_vals["bank"] = self.cbt_total if self.payment_option != "cash" else 0
                pl_vals["res_model"] = "cbt.receipt"
                pl_vals["res_id"] = self.id
                self.env["profit.loss"].create(pl_vals)
            return self.write(vals)

    def unlink(self):
        for receipt in self:
            if receipt.state == "validated":
                raise UserError("Not allowed to delete the validated receipt")
        return super(SicaCbtReceipt, self).unlink()


SicaCbtReceipt()

class SicaReceipt(models.Model):
    _name = "sica.receipt"
    _description = "SICA Receipt Report"
    _order = "id desc"

    sica_cbt_id = fields.Many2one("sica.cbt.receipt", string="SICA/CBT Receipt")
    membership_no = fields.Char(related="sica_cbt_id.membership_no", store=True, string="Membership No.")
    member_name = fields.Char(related="sica_cbt_id.member_name", store=True, string="Member's Name")
    receipt_no = fields.Char(related="sica_cbt_id.sica_receipt_no", store=True, string="Receipt No")
    receipt_date = fields.Date(related="sica_cbt_id.receipt_date", store=True, string="Receipt Date")
    company_id = fields.Many2one('res.company', related="sica_cbt_id.company_id", store=True)
    currency_id = fields.Many2one('res.currency', related="sica_cbt_id.currency_id", store=True)
    total_amount = fields.Monetary(currency_id="currency_id", related="sica_cbt_id.sica_total", store=True, string="Total Amount")

SicaReceipt()

class CbtReceipt(models.Model):
    _name = "cbt.receipt"
    _description = "CBT Receipt Report"
    _order = "id desc"

    sica_cbt_id = fields.Many2one("sica.cbt.receipt", string="SICA/CBT Receipt")
    membership_no = fields.Char(related="sica_cbt_id.membership_no", store=True, string="Membership No.")
    member_name = fields.Char(related="sica_cbt_id.member_name", store=True, string="Member's Name")
    receipt_no = fields.Char(related="sica_cbt_id.cbt_receipt_no", store=True, string="Receipt No")
    receipt_date = fields.Date(related="sica_cbt_id.receipt_date", store=True, string="Receipt Date")
    company_id = fields.Many2one('res.company', related="sica_cbt_id.company_id", store=True)
    currency_id = fields.Many2one('res.currency', related="sica_cbt_id.currency_id", store=True)
    total_amount = fields.Monetary(currency_id="currency_id", related="sica_cbt_id.cbt_total", store=True, string="Total Amount")

CbtReceipt()