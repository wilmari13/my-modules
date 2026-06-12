from odoo import models, fields

class AccountRetentionRule(models.Model):
    _name = 'account.retention.rule'
    _description = 'Reglas de Retención de Impuestos'

    name = fields.Char(string='Nombre de la Regla', required=True)
    
    fiscal_position_id = fields.Many2one(
        'account.fiscal.position', 
        string='Posición Fiscal', 
        required=True,
        help="Posición fiscal que activará esta regla."
    )
    
    tax_ids = fields.Many2many(
        'account.tax',
        string='Impuestos de Retención',
        required=True,
        domain="[('amount', '<', 0)]",
        help="Impuestos que se añadirán a las líneas de la factura."
    )
    
    min_amount = fields.Float(
        string='Monto Mínimo', 
        default=0.0, 
        help="Monto mínimo para aplicar la retención."
    )
