from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        """ Aplica impuestos de retención a las líneas de la factura basado en reglas, antes de publicar """
        for move in self:
            if move.move_type in ('out_invoice', 'in_invoice', 'out_refund', 'in_refund'):
                fiscal_position = move.fiscal_position_id or move.partner_id.property_account_position_id
                
                if fiscal_position:
                    rule = self.env['account.retention.rule'].search([
                        ('fiscal_position_id', '=', fiscal_position.id)
                    ], limit=1)

                    if rule and move.amount_untaxed >= rule.min_amount:
                        rule_tax_ids = rule.tax_ids.ids
                        
                        if rule_tax_ids:
                            lines = move.invoice_line_ids.filtered(lambda l: l.display_type == 'product' or not l.display_type)
                            
                            for line in lines:
                                taxes_to_add = [tax_id for tax_id in rule_tax_ids if tax_id not in line.tax_ids.ids]
                                if taxes_to_add:
                                    line.tax_ids = [(4, tax_id) for tax_id in taxes_to_add]

        return super(AccountMove, self).action_post()
