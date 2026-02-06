from odoo import models, fields, api

class ISPBill(models.Model):
    _name = 'isp.bill'
    _description = 'ISP Monthly Bill'
    _order = 'date_from desc'
    _inherit = ['mail.thread']

    name = fields.Char(string="Bill Reference", required=True, copy=False, readonly=True, default='New')
    provider_id = fields.Many2one('isp.provider', string="Service Provider", required=True)
    period_name = fields.Char(string="Billing Period")
    date_from = fields.Date(string="Billing Period Start", required=True)
    date_to = fields.Date(string="Billing Period End", required=True)
    total_days = fields.Integer(string="Total Days")
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Payment Requested'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled')
    ], string="Status", default='draft', tracking=True)

    line_ids = fields.One2many('isp.bill.line', 'bill_id', string="Bill Details")
    
    total_amount = fields.Float(string="Total Amount", compute="_compute_total", store=True)
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)


    summary_notes = fields.Text(string="Billing Summary", compute="_compute_bill_summary")

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

    @api.depends('line_ids.amount', 'line_ids.service_type_id')
    def _compute_bill_summary(self):
        for bill in self:
            summary_text = ""
            # Dictionary to store counts and totals
            # Structure: { 'Service Name': {'count': 0, 'total': 0.0} }
            stats = {}
            
            for line in bill.line_ids:
                if not line.service_type_id:
                    continue
                
                type_name = line.service_type_id.name
                if type_name not in stats:
                    stats[type_name] = {'count': 0, 'total': 0.0}
                
                stats[type_name]['count'] += 1
                stats[type_name]['total'] += line.amount
            
            # Build the string: "5 service 5G : 4500 SAR"
            summary_parts = []
            for name, data in stats.items():
                summary_parts.append(f"{data['count']} service {name} : {data['total']:.2f} SAR")
            
            bill.summary_notes = "\n".join(summary_parts)

class ISPBillLine(models.Model):
    _name = 'isp.bill.line'
    _description = 'ISP Bill Line'

    bill_id = fields.Many2one('isp.bill', ondelete='cascade')
    service_id = fields.Many2one('isp.service', string="Service / Account", required=True)
    
    # Helpful related fields for the manager to see at a glance
    billing_account_number = fields.Char(related='service_id.billing_account_number', string="Account No.")
    line_number = fields.Char(related='service_id.line_number', string="Line No.")

    service_type_id = fields.Many2one(
        'isp.service.type', 
        related='service_id.service_type_id', 
        string="Service Type"
    )
    assign_employee_id = fields.Many2one(
        'hr.employee', 
        related='service_id.assign_employee_id', 
        string="Assigned Employee"
    )
    branch_id = fields.Many2one(
        'res.company', 
        related='service_id.branch_id', 
        string="Branch"
    )
    assign_department_id = fields.Many2one(
        'hr.department', 
        related='service_id.assign_department_id', 
        string="Department"
    )
    
    amount = fields.Float(string="Amount Due", required=True)