from odoo import models, fields, api
from odoo.exceptions import UserError
import io
import base64
import pdfplumber
import zipfile
import csv
import re

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
        self.ensure_one()
        try:
            file_bytes = base64.b64decode(self.file_data)
            pdf_file = io.BytesIO(file_bytes)
        except Exception:
            raise UserError("Could not decode the PDF file.")

        bill = self._create_isp_bill()

        bill.name = self.file_name.replace('.pdf', '')

        with pdfplumber.open(pdf_file) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() + "\n"
            
            lines = full_text.splitlines()
            services = self.env['isp.service'].search([('service_provider_id', '=', self.provider_id.id)])
            
            for service in services:
                if not service.line_number:
                    continue
                
                for i, line in enumerate(lines):
                    # We look for the exact service number line
                    if service.line_number.strip() == line.strip():
                        print(f"Target Number Found: {line}")
                        
                        # We check the VERY NEXT line for the amounts
                        if i + 1 < len(lines):
                            next_line = lines[i+1]
                            print(f"Data Line Found: {next_line}")
                            
                            parts = next_line.split()
                            # Based on your finding: "0.00 138.00 ..." 
                            # 138.00 is at index 1 (the 2nd value)
                            try:
                                if len(parts) >= 2:
                                    raw_amount = parts[1] # Take 2nd value
                                    
                                    # Clean and convert to float
                                    # Remove any non-numeric characters except dots
                                    clean_amount = "".join(c for c in raw_amount if c.isdigit() or c == '.')
                                    due_amount = float(clean_amount)

                                    self.env['isp.bill.line'].create({
                                        'bill_id': bill.id,
                                        'service_id': service.id,
                                        'amount': due_amount,
                                    })
                                    print(f"Successfully Imported: {service.line_number} -> {due_amount}")
                            except (ValueError, IndexError) as e:
                                print(f"Could not parse amount on next line for {service.line_number}: {e}")
                        break
        return bill  
        


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
    
