from odoo import models, fields, api

class ISPBill(models.Model):
    _name = 'isp.bill'
    _description = 'ISP Monthly Bill'
    _order = 'date_from desc'
    _inherit = ['mail.thread']

    name = fields.Char(string="Bill Reference", required=True, copy=False, readonly=True, default='New')
    provider_id = fields.Many2one('isp.provider', string="Service Provider", required=True)
    
    date_from = fields.Date(string="Billing Period Start", required=True)
    date_to = fields.Date(string="Billing Period End", required=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Payment Requested'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled')
    ], string="Status", default='draft', tracking=True)

    line_ids = fields.One2many('isp.bill.line', 'bill_id', string="Bill Details")
    
    total_amount = fields.Float(string="Total Amount", compute="_compute_total", store=True)
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)

    @api.depends('line_ids.amount')
    def _compute_total(self):
        for bill in self:
            bill.total_amount = sum(line.amount for line in bill.line_ids)

    def action_confirm(self):
        self.write({'state': 'requested'})

    def action_post_payment(self):
        """ This method will be called when finance confirms payment. 
            It will then create the entries in isp.payment.history """
        for bill in self:
            for line in bill.line_ids:
                self.env['isp.payment.history'].create({
                    'service_id': line.service_id.id,
                    'amount': line.amount,
                    'date_from': bill.date_from,
                    'date_to': bill.date_to,
                    'period_name': f"{bill.provider_id.name} - {bill.date_from.strftime('%b %Y')}"
                })
            bill.write({'state': 'paid'})

class ISPBillLine(models.Model):
    _name = 'isp.bill.line'
    _description = 'ISP Bill Line'

    bill_id = fields.Many2one('isp.bill', ondelete='cascade')
    service_id = fields.Many2one('isp.service', string="Service / Account", required=True)
    
    # Helpful related fields for the manager to see at a glance
    billing_account_number = fields.Char(related='service_id.billing_account_number', string="Account No.")
    line_number = fields.Char(related='service_id.line_number', string="Line No.")
    
    amount = fields.Float(string="Amount Due", required=True)