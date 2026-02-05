from odoo import models, fields, api
from odoo.exceptions import UserError
import io
import base64
import pdfplumber
import zipfile
import csv

class ISPInvoiceImportWizard(models.TransientModel):
    _name = 'isp.invoice.import.wizard'
    _description = "ISP Invoice Import Wizard"


    provider_id = fields.Many2one('isp.provider', string="Provider", required=True)


    period_name = fields.Char(required=True)
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)

    # We make this readonly so the user doesn't accidentally change the math
    total_days = fields.Integer(string="Total Days", compute="_compute_total_days", store=True, readonly=True)
    file_name = fields.Char(string="File Name") # Odoo uses this to know the extension
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
    # ok we have isp.bill and isp.bill.line models to store the data
        if self.file_name.endswith('.pdf'):
            self._import_from_pdf()
        elif self.file_name.endswith('.zip'):
            self._import_from_zip()
        elif self.file_name.endswith('.csv'):
            self._import_from_csv()
        else:
            raise UserError("Unsupported file type. Please upload a PDF, ZIP, or CSV file.")
        
    def _import_from_pdf(self):
        print("Importing from PDF...")
        
        # first the invoice maybe in arabic or english so we need to detect the language
        # mobily invoices are in arabic and one pdf has all the services so
        # we take the line_number from isp.service and search for it in the pdf text
        # if we find it we move left side the 6 value is the due amount for that service
        # 1. Decode and wrap the file data
        try:
            file_bytes = base64.b64decode(self.file_data)
            pdf_file = io.BytesIO(file_bytes)
        except Exception:
            raise UserError("Could not decode the PDF file.")

        # 2. Create the Master Bill record
        bill = self._create_isp_bill()

        # 3. Process the PDF
        with pdfplumber.open(pdf_file) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() + "\n"
            
            # Search for services belonging to this provider
            services = self.env['isp.service'].search([('service_provider_id', '=', self.provider_id.id)])
            
            for service in services:
                if service.line_number and service.line_number in full_text:
                    # find the line containing the line_number
                    for line in full_text.splitlines():
                        if service.line_number in line:
                            parts = line.split()
                            try:
                                # Logic: Move left 6 positions to find amount
                                # We also handle the Arabic/English comma decimal separator
                                raw_amount = parts[parts.index(service.line_number) - 6]
                                due_amount = float(raw_amount.replace(',', ''))
                                
                                # 4. Create the Bill Line record in the database
                                self.env['isp.bill.line'].create({
                                    'bill_id': bill.id,
                                    'service_id': service.id,
                                    'amount': due_amount,
                                })
                                print(f"Success: {service.line_number} -> {due_amount}")
                            
                            except (ValueError, IndexError):
                                print(f"Could not extract due amount for {service.line_number}")
                            break
        
        return bill # Return the bill so action_import can open it
        


    def _import_from_zip(self):
        print("Importing from ZIP...")
        

    def _import_from_csv(self):
        print("Importing from CSV...")
        




    def _create_isp_bill(self):
        # This method will create the isp.bill record and return it so we can link the lines to it

        return self.env['isp.bill'].create({
            'provider_id': self.provider_id.id,
            'period_name': self.period_name,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'total_days': self.total_days
        })
    
