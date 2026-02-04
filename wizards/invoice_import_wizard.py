from odoo import models, fields, api

class ISPInvoiceImportWizard(models.TransientModel):
    _name = 'isp.invoice.import.wizard'
    _description = "ISP Invoice Import Wizard"


    provider_type = fields.Selection([
    ('mobily', 'Mobily'),
    ('stc', 'STC')
    ], required=True)


    period_name = fields.Char(required=True)
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)

    # We make this readonly so the user doesn't accidentally change the math
    total_days = fields.Integer(string="Total Days", compute="_compute_total_days", store=True, readonly=True)
    file_data = fields.Binary(required=True)


    @api.depends('date_from', 'date_to')
    def _compute_total_days(self):
        for record in self:
            if record.date_from and record.date_to:
                # Subtracting two dates returns a timedelta object
                delta = record.date_to - record.date_from
                # We add +1 because usually billing periods are inclusive of both days
                record.total_days = delta.days + 1
            else:
                record.total_days = 0


    def action_import(self):
    # Implementation as specified (pdfplumber / zipfile / csv)
    # first we check the file type is pdf or zip or csv
    # then we process accordingly
    # we go through each ISPService . billing_account_number
    # but sometime one billing_account_number may have multiple services
    # so we need to handle that case as well so we need to search for line_number becouse it is unique per service
    # we need to create Service Bill for each service found in the file
        pass