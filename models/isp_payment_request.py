from odoo import models, fields, api


class PaymentRequest(models.Model):
    _name = 'isp.payment.request'
    _description = 'ISP Payment Request'

    requesting_department = fields.Many2one('hr.department', string='Requesting Department')
    beneficiary = fields.Many2one('isp.provider', string='Beneficiary')
    amount = fields.Float(string='Amount')
    description = fields.Text(string='Description')
    state = fields.Selection([('draft', 'Draft'), ('submitted', 'Submitted'), ('approved', 'Approved'), ('rejected', 'Rejected')], string='Status', default='draft')
    request_date = fields.Date(string='Request Date', default=fields.Date.context_today)

    department_head_approval = fields.Boolean(string='Department Head Approval')
    finance_manager_approval = fields.Boolean(string='Finance Manager Approval')
    ceo_approval = fields.Boolean(string='CEO Approval')