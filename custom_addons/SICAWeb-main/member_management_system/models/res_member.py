# -*- coding: utf-8 -*-
import os
import shutil
import tempfile

from odoo import models, fields, api
from odoo.exceptions import UserError

try:
   import qrcode
except ImportError:
   qrcode = None
try:
   import base64
except ImportError:
   base64 = None
from io import BytesIO
from datetime import date, datetime, timedelta



class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    member_id = fields.Many2one('res.member')


class MemberWork(models.Model):
    _name = 'member.work'
    _description = 'Member Works'

    project_name = fields.Char()
    year = fields.Char()
    designation = fields.Char()
    member_id = fields.Many2one('res.member')
    request_type = fields.Selection([
        ('Create', 'Create'),
        ('Update', 'Update'),
        ('Delete', 'Delete')
    ])
    approve_status = fields.Selection([
        ('Waiting_for_approval', 'Waiting for Approval'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ])
    duplicate_member_id = fields.Many2one('res.member')
    work_id = fields.Many2one('member.work')
    format = fields.Char(string='Format')
    dop_name = fields.Char(string='DOP Name')
    image = fields.Binary(string="Image")
    proof_image = fields.Binary(string="Proof Image")
    weblink = fields.Char(string="Weblink")
    language = fields.Char(string="Language")

    def action_approve(self):
        user_id = self.env.user.id
        for rec in self:
            if rec.request_type == 'Create':
                rec.member_id = rec.duplicate_member_id
                rec.approve_status = 'Approved'
                self.env['member.work.status'].sudo().create({
                    'user_id': user_id,
                    'member_id': rec.member_id.id,
                    'status': 'Approved',
                    'date': datetime.now(),
                    'project_name': rec.project_name,
                    'year': rec.year,
                    'designation': rec.designation,
                    'request_type': rec.request_type,
                    'format': rec.format,
                    'dop_name': rec.dop_name,
                    'image': rec.image,
                    'proof_image': rec.proof_image,
                })
            elif rec.request_type == 'Update':
                if rec.request_type == 'Update':
                    self.env['member.work.status'].sudo().create({
                        'user_id': user_id,
                        'member_id': rec.member_id.id,
                        'status': 'Approved',
                        'date': datetime.now(),
                        'project_name': rec.project_name,
                        'year': rec.year,
                        'designation': rec.designation,
                        'request_type': rec.request_type,
                        'format': rec.format,
                        'dop_name': rec.dop_name,
                        'image': rec.image,
                        'proof_image': rec.proof_image,
                    })
                    rec.member_id = rec.duplicate_member_id
                    rec.work_id.sudo().unlink()
                    rec.approve_status = 'Approved'
            else:
                if rec.request_type == 'Delete':
                    self.env['member.work.status'].sudo().create({
                        'user_id': user_id,
                        'member_id': rec.member_id.id,
                        'status': 'Approved',
                        'date': datetime.now(),
                        'project_name': rec.project_name,
                        'year': rec.year,
                        'designation': rec.designation,
                        'request_type': rec.request_type,
                        'format': rec.format,
                        'dop_name': rec.dop_name,
                        'image': rec.image,
                        'proof_image': rec.proof_image,
                    })
                    rec.sudo().unlink()
                    rec.approve_status = 'Approved'


    def action_reject(self):
        user_id = self.env.user.id
        for rec in self:
            rec.approve_status = 'Rejected'
            self.env['member.work.status'].sudo().create({
                'user_id': user_id,
                'member_id': rec.duplicate_member_id.id,
                'status': 'Rejected',
                'date': datetime.now(),
                'project_name': rec.project_name,
                'year': rec.year,
                'designation': rec.designation,
                'request_type': rec.request_type,
                'format': rec.format,
                'dop_name': rec.dop_name,
                'image': rec.image,
                'proof_image': rec.proof_image,
            })


class MemberWorkApprove(models.Model):
    _name = 'member.work.status'
    _description = 'Member Approve Status'

    user_id = fields.Many2one('res.users', string='Responsible', readonly=True)
    member_id = fields.Many2one('res.member', string='Member', readonly=True)
    status = fields.Selection([
        ('Waiting_for_approval', 'Waiting for Approval'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ], readonly=True)
    project_name = fields.Char()
    year = fields.Char()
    designation = fields.Char()
    request_type = fields.Selection([
        ('Create', 'Create'),
        ('Update', 'Update'),
        ('Delete', 'Delete')
    ])
    format = fields.Char(string='Format')
    dop_name = fields.Char(string='DOP Name')
    image = fields.Binary(string="Image")
    proof_image = fields.Binary(string="Proof Image")
    date = fields.Datetime(string='Date', readonly=True)
    remark = fields.Html(string='Remarks')



class Members(models.Model):
    _inherit = ["mail.thread", "mail.activity.mixin", "format.address.mixin", "avatar.mixin"]
    _name = "res.member"
    _description = "Members Management"
    _rec_name = "display_name"
    _order = "id desc"

    @api.depends('name', 'membership_no', 'alias_name')
    def _compute_display_name(self):
        for member in self:
            display_name = "[%s] %s" % (
            member.membership_no, member.name) if member.membership_no else member.name
            if member.alias_name:
                display_name += ' aka %s'% member.alias_name
            member.display_name = display_name

    def get_count_sica_cbt(self):
        for member in self:
            member.sica_cbt_receipts = self.env["sica.cbt.receipt"].search_count([("member_id", "=", member.id)])


    # General Details
    state = fields.Selection([
        ("active", "Live"),
        ("debar", "Debar"),
        ("inactive", "Inactive"),
        ("expired", "Expired")
    ], default="active", required=True, tracking=True, string="Status")
    sica_cbt_receipts = fields.Integer(compute="get_count_sica_cbt", string="SICA/CBT Receipts")
    name = fields.Char(required=True, tracking=True, string="Name")
    alias_name = fields.Char(string="Screen Name")
    membership_no = fields.Char(default="/", copy=False, readonly=False, tracking=True, string="Membership No.")
    display_name = fields.Char(compute='_compute_display_name', store=True, index=True)
    dob = fields.Date(string="Date of Birth", tracking=True)
    gender = fields.Selection([
        ("male", "Male"),
        ("female", "Female"),
        ("others", "Others")
    ], tracking=True, string="Gender")
    grade = fields.Selection([
        ("junior", "Junior"),
        ("staff", "Staff"),
        ("life", "Life"),
        ("active", "Active"),
        ("associate", "Associate"),
    ], required=True, tracking=True, string="Grade")
    date_of_join = fields.Date(string="Date of Join", tracking=True)
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    lcf = fields.Monetary(string="LCF", currency_field="currency_id", tracking=True)
    loans = fields.Monetary(string="Loans", currency_field="currency_id", tracking=True)
    aids = fields.Monetary(string="Aids", currency_field="currency_id", tracking=True)
    sica_fee = fields.Monetary(string="SICA Fee", currency_field="currency_id", tracking=True)
    cbt_fee = fields.Monetary(string="CBT Fee", currency_field="currency_id", tracking=True)
    paid_till = fields.Char(string="Paid Till", tracking=True)
    photo_submitted = fields.Boolean(string="Photo Submitted", tracking=True)
    proof_submitted = fields.Boolean(string="Proof Submitted", tracking=True)
    pensioner = fields.Boolean(string="Pensioner", tracking=True)
    cam_life = fields.Boolean(string="CAM Life", tracking=True)
    expired_date = fields.Date(string="Expired Date", tracking=True)
    token = fields.Char(string="Device firebase token", readonly=False)
    fefsi_card = fields.Char(string="FEFSI Card")

    # Personal Details
    father_name = fields.Char(copy=False, tracking=True, string="Father's Name")
    mother_name = fields.Char(copy=False, tracking=True, string="Mother's Name")
    blood_group = fields.Selection([
        ("A+ve", "A+ve"),
        ("A-ve", "A-ve"),
        ("A1+ve", "A1+ve"),
        ("A1-ve", "A1-ve"),
        ("A1B+ve", "A1B+ve"),
        ("A1B-ve", "A1B-ve"),
        ("A2B+ve", "A2B+ve"),
        ("B+ve", "B+ve"),
        ("B-ve", "B-ve"),
        ("AB+ve", "AB+ve"),
        ("AB-ve", "AB-ve"),
        ("O+ve", "O+ve"),
        ("O-ve", "O-ve"),
    ], copy=False, tracking=True, string="Blood Group")
    nominee1 = fields.Char(string="Nominee1", tracking=True)
    nominee1_relationship = fields.Selection([
        ("father", "Father"),
        ("mother", "Mother"),
        ("spouse", "Spouse"),
        ("son", "Son"),
        ("daughter", "Daughter"),
        ("brother", "Brother"),
        ("sister", "Sister"),
        ("cousin", "Cousin"),
        ("grandfather", "Grand Father"),
        ("grandmother", "Grand Mother"),
        ("daughter/son", "Daughter/Son"),
        ("others", "Others"),
    ], string="Nominee1 Relationship")
    nominee1_others = fields.Char(copy=False, string="Nominee1 Others")
    nominee1_photo = fields.Binary(string="Nominee1 Photo")
    nominee1_fname = fields.Char(string="Nominee1 Filename")
    nominee2 = fields.Char(string="Nominee2", tracking=True)
    nominee2_relationship = fields.Selection([
        ("father", "Father"),
        ("mother", "Mother"),
        ("spouse", "Spouse"),
        ("son", "Son"),
        ("daughter", "Daughter"),
        ("brother", "Brother"),
        ("sister", "Sister"),
        ("cousin", "Cousin"),
        ("grandfather", "Grand Father"),
        ("grandmother", "Grand Mother"),
        ("daughter/son", "Daughter/Son"),
        ("others", "Others"),
    ], string="Nominee2 Relationship")
    nominee2_others = fields.Char(copy=False, string="Nominee2 Others")
    nominee2_photo = fields.Binary(string="Nominee2 Photo")
    nominee2_fname = fields.Char(string="Nominee2 Filename")

    # Contact Details - To show residential and permanent address
    street = fields.Char(string="Res Street")
    street2 = fields.Char(string="Res Area")
    zip = fields.Char(change_default=True, string="Res Pin Code")
    city = fields.Char(string="Res City")
    state_id = fields.Many2one("res.country.state", string='Res State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Res Country', ondelete='restrict')

    address_same_as_res = fields.Boolean(string="Copy Res Address")
    per_street = fields.Char(string="Per Street")
    per_street2 = fields.Char(string="Per Area")
    per_zip = fields.Char(string="Per Pin Code", change_default=True)
    per_city = fields.Char(string="Per City")
    per_state_id = fields.Many2one("res.country.state", string='Per State', ondelete='restrict',
                                   domain="[('country_id', '=?', per_country_id)]")
    per_country_id = fields.Many2one('res.country', string='Per Country', ondelete='restrict')
    contact1 = fields.Char(string="Contact No. 1")
    contact2 = fields.Char(string="Contact No. 2")
    email = fields.Char(string="Email ID")
    subscription_end_date = fields.Date(string='Subscription End Date')

    single_address_line = fields.Text('Address', compute='_get_address')

    # Official Details
    medical_card_no = fields.Char(string="Medical Card #", copy=False)
    nalavariam_reg_no = fields.Char(string="Nalavariam Reg #", copy=False)
    bank_acc_no = fields.Char(string="Bank Acc No.", tracking=True, copy=False)
    bank_name_ifsc = fields.Char(string="Bank Name/IFSC", tracking=True, copy=False)
    remarks = fields.Char(string="Remarks", tracking=True, copy=False)

    # Attachments
    aadhaar_card = fields.Binary(string="Aadhaar Card")
    aadhaar_fname = fields.Char(string="Aadhaar Filename")

    membership_form = fields.Binary(string="Membership Form")
    membership_form_file_name = fields.Char(string="Membership Form File Name")
    membership_id_card = fields.Binary(string="Membership ID Card")
    membership_id_card_fname = fields.Char(string="Membership ID Card Filename")
    other_attachments = fields.Binary(string="Other Attachments")
    other_fname = fields.Char(string="Other Filename")
    qr_code = fields.Binary(compute="_generate_qr")
    qr_code_preview = fields.Binary()
    # qr_code = fields.Binary()
    attachment_id = fields.Many2one("ir.attachment")
    attachment_file_name = fields.Char()
    designation = fields.Char()
    medium = fields.Char()
    skills = fields.Text()
    experience = fields.Char()
    portifolio_link = fields.Char()
    facebook_link = fields.Char()
    instagram_link = fields.Char()
    youtube_link = fields.Char()
    twitter_link = fields.Char()
    linkedin_link = fields.Char()
    other_link = fields.Char(string="Other Link")
    vimeo_link = fields.Char(string="Vimeo Link")
    imdb_link = fields.Char()
    work_ids = fields.One2many('member.work', 'member_id')
    notes = fields.Text()
    show_social_link = fields.Boolean()
    show_discussion = fields.Boolean()
    show_all_members = fields.Boolean()
    show_all_works = fields.Boolean()
    show_job_seeker = fields.Boolean()
    show_job_provider = fields.Boolean()
    show_grievance_forum = fields.Boolean()
    show_shooting = fields.Boolean()
    show_shooting_dop = fields.Boolean()
    medium_id = fields.Many2one('member.medium')
    profile_photo_data = fields.Char()
    contact_privacy = fields.Boolean()
    notes_privacy = fields.Boolean()
    contact_show = fields.Selection([
        ('Private', 'Private'),
        ('Public', 'Public')
    ], string="Contact Privacy")
    notes_show = fields.Selection([
        ('Private', 'Private'),
        ('Public', 'Public')
    ], string="Notes Privacy")
    show_notes = fields.Boolean()
    show_contact = fields.Boolean()
    educational_qualification = fields.Char()
    document_ids = fields.One2many('ir.attachment', 'member_id')
    qr_code_filename = fields.Char(string='QR Code Filename', readonly=True)
    active = fields.Boolean(default=True)

    @api.depends('street', 'street2', 'city', 'state_id', 'zip', 'country_id')
    def _get_address(self):
        for rec in self:
            if rec:
                address = str(rec.street) + ' ' + str(rec.street2) + '\n' + str(rec.city) + ' ' +  str(rec.state_id.name) + ' ' + '(' + str(rec.state_id.code) + ')' + ' ' + str(rec.zip) + '\n' + str(rec.country_id.name)
                rec.single_address_line = address.replace('False', '')
            else:
                rec.single_address_line = None

    def _generate_qr(self):
        for member in self:
            if qrcode and base64:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=3,
                    border=4,
                )
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url.image')
                if base_url and member.attachment_id:
                    if base_url[-1] == '/':
                        base_url = base_url[:-1]
                    base_url += '/member/qr_code/%s' % member.membership_no
                    qr.add_data(base_url)
                    qr.make(fit=True)
                    img = qr.make_image()
                    temp = BytesIO()
                    img.save(temp, format="PNG")
                    filename = f"{member.membership_no}-{member.name}-qr-code.png"
                    member.qr_code_filename = filename
                    qr_image = base64.b64encode(temp.getvalue())
                    member.qr_code = qr_image
                    member.qr_code_preview = qr_image
                else:
                    member.qr_code = False
                    member.qr_code_preview = False
            else:
                member.qr_code = False
                member.qr_code_preview = False

    def generate_pdf(self):
        result, format = self.env.ref('member_management_system.action_report_member_pdf')._render_qweb_pdf(res_ids=self.ids)
        result = base64.b64encode(result)
        report_name = "Member Details %s"% str(self.membership_no)
        vals = {}
        vals['name'] = report_name + '.pdf'
        vals['type'] = 'binary'
        vals['datas'] = result
        vals['store_fname'] = report_name + '.pdf'
        vals['mimetype'] = 'application/pdf'
        vals['index_content'] = 'image'
        vals['res_model'] = 'res.member'
        vals['res_id'] = self.membership_no
        vals['public'] = True
        attachment = self.env['ir.attachment'].search([('res_model', '=', 'res.member'), ('res_id', '=', self.membership_no), ('name', '=', report_name + '.pdf')], limit=1)
        if attachment:
            attachment.write(vals)
        else:
            attachment = self.env['ir.attachment'].create(vals)
            self.write({'attachment_id': attachment.id})
            self._generate_qr()
        return True


    @api.model
    def create(self, vals):
        if vals.get("membership_no", "/") == "/":
            vals["membership_no"] = self.env["ir.sequence"].next_by_code("res.member")
        return super(Members, self).create(vals)

    # def write(self, vals):
    #     res = super(Members, self).write(vals)
    #     if vals:
    #         self.generate_pdf()
    #     return res

    @api.onchange('state_id')
    def _onchange_state_id(self):
        if self.state_id:
            self.country_id = self.state_id.country_id

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id and self.state_id and self.country_id != self.state_id.country_id:
            self.state_id = False

    @api.onchange('per_state_id')
    def _onchange_per_state_id(self):
        if self.per_state_id:
            self.per_country_id = self.per_state_id.country_id

    @api.onchange('per_country_id')
    def _onchange_per_country_id(self):
        if self.per_country_id and self.per_state_id and self.per_country_id != self.per_state_id.country_id:
            self.per_state_id = False

    @api.onchange('address_same_as_res', 'street', 'street2', 'zip', 'city', 'state_id', 'country_id')
    def _onchange_address_same_as_res(self):
        if self.address_same_as_res:
            self.per_street = self.street
            self.per_street2 = self.street2
            self.per_zip = self.zip
            self.per_city = self.city
            self.per_state_id = self.state_id and self.state_id.id
            self.per_country_id = self.country_id and self.country_id.id

    def button_inactive(self):
        return self.write({"state": "inactive"})

    def button_active(self):
        return self.write({"state": "active"})

    def button_debar(self):
        return self.write({"state": "debar"})

    def button_expired(self):
        return self.write({"state": "expired", "expired_date": fields.Date.today()})

    def get_residential_address(self):
        address = ''
        if self.street:
            address += '%s\n' % self.street
        if self.street2:
            address += '%s\n' % self.street2
        if self.city and self.zip and self.state_id:
            address += '%s %s\n%s\n' % (self.city, self.zip, self.state_id.name)
        elif self.city and self.zip:
            address += '%s %s\n' % (self.city, self.zip)
        elif self.city and self.state_id:
            address += '%s %s\n' % (self.city, self.state_id.name)
        elif self.zip and self.state_id:
            address += '%s %s\n' % (self.state_id.name, self.zip)
        elif self.city:
            address += '%s\n' % self.city
        elif self.zip:
            address += '%s\n' % self.zip
        elif self.state_id:
            address += '%s\n' % self.state_id.name
        return address[:-1]

    def view_sica_cbt_receipts(self):
        self.ensure_one()
        result = {
            "type": "ir.actions.act_window",
            "res_model": "sica.cbt.receipt",
            "domain": [("member_id", "=", self.id)],
            "context": {"create": False, "edit": False, "delete": False},
            "name": "SICA/CBT Receipts",
            'view_mode': 'tree,form',
        }
        return result

    def migrate_permanent_address(self):
        for member in self.env["res.member"].search([]):
            if member.state_id:
                member.write({"country_id": member.state_id.country_id.id})
            if member.address_same_as_res:
                vals = {}
                vals["per_street"] = member.street
                vals["per_street2"] = member.street2
                vals["per_zip"] = member.zip
                vals["per_city"] = member.city
                vals["per_state_id"] = member.state_id and member.state_id.id
                vals["per_country_id"] = member.country_id and member.country_id.id
                member.write(vals)
            elif member.per_state_id:
                member.write({"per_country_id": member.per_state_id.country_id.id})
        return True

Members()
