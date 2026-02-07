from odoo import models, fields, api


class PaymentRequest(models.Model):
    _name = 'isp.payment.request'
    _description = 'ISP Payment Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    requesting_department = fields.Many2one('hr.department', string='Requesting Department')
    beneficiary = fields.Many2one('isp.provider', string='Beneficiary')
    bill_id = fields.Many2one('isp.bill', string="Related Bill", tracking=True)
    # if the user seelct the bill the system will get the amount from the bill bill_id.total_amount
    amount = fields.Float(string='Amount', digits=(16, 2), tracking=True)

    # \n bill_id.summary_notes
    description = fields.Text(string='Description', default='Payment request for ISP services', tracking=True)
    state = fields.Selection([('draft', 'Draft'), ('submitted', 'Submitted'), ('approved', 'Approved'), ('rejected', 'Rejected')], string='Status', default='draft')
    request_date = fields.Date(string='Request Date', default=fields.Date.context_today)

    department_head_approval = fields.Boolean(string='Department Head Approval')
    finance_manager_approval = fields.Boolean(string='Finance Manager Approval')
    ceo_approval = fields.Boolean(string='CEO Approval')



    @api.onchange('bill_id')
    def _onchange_bill_id(self):
        """ Automatically fetch total amount when bill is selected """
        if self.bill_id:
            # Get amount from the related bill
            self.amount = self.bill_id.total_amount
        # Sync beneficiary if it's set on the bill
            if self.bill_id.provider_id:
                self.beneficiary = self.bill_id.provider_id
            # Build description
            base_text = 'Payment request for ISP services'
            if self.bill_id.summary_notes:
                self.description = base_text + '\n' + self.bill_id.summary_notes
            else:
                self.description = base_text

    
    @api.model_create_multi
    def create(self, vals_list):
        # 1. Standard Odoo Create
        records = super(PaymentRequest, self).create(vals_list)
        
        # 2. After saving, update the linked bills to 'requested'
        for record in records:
            if record.bill_id:
                record.bill_id.state = 'requested'
        return records

    def write(self, vals):
        # 1. Standard Odoo Write
        res = super(PaymentRequest, self).write(vals)
        
        # 2. If the bill_id was changed during this save
        if 'bill_id' in vals:
            for record in self:
                if record.bill_id:
                    record.bill_id.state = 'requested'
        return res
    
    def unlink(self):
        """ This triggers when you delete the Payment Request """
        for record in self:
            if record.bill_id:
                # Set the bill back to draft so it can be requested again later
                record.bill_id.state = 'draft'
        return super(PaymentRequest, self).unlink()