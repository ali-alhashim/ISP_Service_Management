from odoo import models, fields

class ISPInvoiceImportWizard(models.TransientModel):
    _name = 'isp.invoice.import.wizard'


    provider_type = fields.Selection([
    ('mobily', 'Mobily'),
    ('stc', 'STC')
    ], required=True)


    period_name = fields.Char(required=True)
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    file_data = fields.Binary(required=True)


    def action_import(self):
    # Implementation as specified (pdfplumber / zipfile / csv)
        pass