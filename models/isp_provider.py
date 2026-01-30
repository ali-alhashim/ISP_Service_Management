from odoo import models, fields

class ISPProvider(models.Model):
    _name = 'isp.provider'
    _description = 'ISP Provider'

    name = fields.Char(string='Provider Name', required=True)
    notes = fields.Text(string='Notes')
    service_ids = fields.One2many('isp.service', 'service_provider_id', string='Services Provided')