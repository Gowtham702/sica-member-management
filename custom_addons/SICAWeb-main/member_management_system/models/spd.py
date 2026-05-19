from odoo import fields,models,api,_

class SpdCategory(models.Model):
    _name = 'spd.category'
    _description = 'SPD Category'

    name = fields.Char(string='Category Name')
    description = fields.Text()
    active = fields.Boolean(default=True, string='Active')

class SubCategory(models.Model):
    _name = 'spd.sub.category'
    _description = 'SPD Sub Category'

    name = fields.Char(string='Name', required=True)
    company_name = fields.Char(string='Company Name')
    active = fields.Boolean(default=True, string='Active')
    vendor_type = fields.Selection([
        ('vendor', 'Vendor'),
        ('supplier', 'Supplier'),
        # Add more choices as needed
    ], string='Vendor Type')
    phone_number = fields.Char(string='Phone Number')
    email = fields.Char(string='Email')
    photo = fields.Binary(attachment=True,
                          help='Upload an image')
    website = fields.Char(string='Website')
    address = fields.Text(string='Address')
    product_id = fields.Many2one('spd.product')
    category_id = fields.Many2one('spd.category')
    location = fields.Char(string='Location')
    product_ids = fields.One2many('product.vendor.line', 'sp_category_id', string='Products')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('subscribed', 'Subscribed'),
        ('unsubscribed', 'Unsubscribed'),
    ], string='Status', default='draft')

    def action_subscribe(self):
        for rec in self:
            rec.state = 'subscribed'

    def action_unsubscribe(self):
        for rec in self:
            rec.state = 'unsubscribed'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

class ProductVendorLine(models.Model):
    _name = 'product.vendor.line'

    sp_category_id = fields.Many2one('spd.sub.category', cascade='ondelete')
    sequence = fields.Integer(string='Sequence', default=lambda self: self._get_default_sequence())
    name = fields.Char(string='Name')
    category_id = fields.Many2one('spd.category')
    description = fields.Text()
    quantity = fields.Integer()
    image = fields.Binary(attachment=True,
                          help='Upload an image')
    image_link = fields.Char('Image Link')

    @api.model
    def _get_default_sequence(self):
        """Compute the next sequence number by default."""
        last_record = self.search([], order='sequence desc', limit=1)
        return (last_record.sequence + 1) if last_record else 1

class ProductProduct(models.Model):
    _name = 'spd.product'
    _description = 'SPD Product'

    name = fields.Char()
    description = fields.Char()
    vendor_ids = fields.One2many('product.vendor', 'product_id')

class ProductVendorList(models.Model):
    _name = 'product.vendor'
    _description = 'Product Description'

    product_id = fields.Many2one('spd.product')
    vendor_id = fields.Many2one('spd.sub.category')
    company_name = fields.Char(string='Company Name', related='vendor_id.company_name')
    vendor_type = fields.Selection([
        ('vendor', 'Vendor'),
        ('supplier', 'Supplier'),
        # Add more choices as needed
    ], string='Vendor Type', related='vendor_id.vendor_type')

    email = fields.Char(string='Email', related='vendor_id.email')

class Spdbannerphoto(models.Model):
    _name = 'spd.banner.photo'
    _description = 'Spd vendor Photo'

    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char()
    photo = fields.Binary(attachment=True,
        help='Upload an image')
    promotion_link = fields.Char()
    description = fields.Char()
    active = fields.Boolean(string="Active", default=True)
