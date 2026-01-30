from odoo import models, fields

class ISPPaymentRequestWizard(models.TransientModel):
    _name = 'isp.payment.request.wizard'


    department_id = fields.Many2one('hr.department', required=True)
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)


    def action_export_excel(self):
    # openpyxl aggregation & download action
        pass