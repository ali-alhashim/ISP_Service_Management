from odoo import models, fields, api


class ISPService(models.Model):
    _name = 'isp.service'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'ISP Service'


    name = fields.Char(compute='_compute_name', store=True)
    service_provider_id = fields.Many2one('isp.provider', required=True)
    service_type_id = fields.Many2one('isp.service.type', required=True)
    line_number = fields.Char(required=True)
    billing_account_number = fields.Char(help='STC Billing Account Number')
    serial_number = fields.Char()

    status = fields.Selection([
    ('active', 'Active'),
    ('deactive', 'Deactive'),
    ('canceled', 'Canceled'),
    ], default='active', tracking=True)

    assign_employee_id = fields.Many2one('hr.employee')
    assign_department_id = fields.Many2one('hr.department')
    branch_id = fields.Many2one('res.company')
    location_partner_id = fields.Many2one('res.partner')
    service_package = fields.Char()
    bandwidth = fields.Char()
    usage_limit = fields.Integer()
    current_usage = fields.Integer()
    remaining_balance = fields.Integer(compute='_compute_remaining', store=True)

    active_date = fields.Date()
    monthly_fee = fields.Monetary()
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    recurring_day = fields.Integer()

    payment_ids = fields.One2many('isp.payment.history', 'service_id')
    notes = fields.Text()


    @api.depends('service_provider_id')
    def _compute_name(self):
        for rec in self:
            rec.name = f"Service - {rec.service_provider_id.name}" if rec.service_provider_id else 'Service'

    @api.depends('usage_limit', 'current_usage')
    def _compute_remaining(self):
        for rec in self:
            rec.remaining_balance = (rec.usage_limit or 0) - (rec.current_usage or 0)