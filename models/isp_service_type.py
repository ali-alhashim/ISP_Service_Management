from odoo import models, fields

class ISPServiceType(models.Model):
    _name = 'isp.service.type'
    _description = 'ISP Service Type'

    name = fields.Char(string='Service Type', required=True)
