from odoo import models, fields

class ISPPaymentRequestWizard(models.TransientModel):
    _name = 'isp.payment.request.wizard'


    department_id = fields.Many2one('hr.department', string="Department", tracking=True)
    employee_id = fields.Many2one('hr.employee', string="Assigned Employee", tracking=True)
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)


    def action_export_excel(self):
    # openpyxl aggregation & download action
        pass