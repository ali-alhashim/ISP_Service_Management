from odoo import models, fields, api


class ISPPaymentHistory(models.Model):
    _name = 'isp.payment.history'
    _description = 'ISP Payment History'


    service_id = fields.Many2one('isp.service', required=True, ondelete='cascade')
    department_id = fields.Many2one('hr.department', compute='_compute_department', store=True)


    period_name = fields.Char()
    date_from = fields.Date()
    date_to = fields.Date()


    amount = fields.Monetary()
    currency_id = fields.Many2one('res.currency', related='service_id.currency_id', store=True)


    invoice_file = fields.Binary()
    tt_document = fields.Binary()


    created_date = fields.Date(default=fields.Date.today)


    @api.depends('service_id.assign_department_id')
    def _compute_department(self):
        for rec in self:
            rec.department_id = rec.service_id.assign_department_id