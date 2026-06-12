from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    risk_level = fields.Selection([
        ('none', 'Sin Riesgo'),
        ('low', 'Bajo'),
        ('medium', 'Medio'),
        ('high', 'Alto')
    ], string='Nivel de Riesgo', compute='_compute_collection_risk', store=True, default='none')

    @api.depends('invoice_date_due', 'amount_residual', 'state', 'payment_state')
    def _compute_collection_risk(self):
        # Cache de reglas para no consultarlas en cada factura dentro del bucle
        rules = self.env['account.collection.alert.rule'].search([])
        today = fields.Date.context_today(self)

        for move in self:
            if move.move_type not in ('out_invoice', 'out_receipt') or move.state != 'posted' or move.payment_state in ('paid', 'in_payment'):
                move.risk_level = 'none'
                continue

            if not move.invoice_date_due or move.invoice_date_due >= today:
                move.risk_level = 'none'
                continue

            # Factura vencida
            days_overdue = (today - move.invoice_date_due).days
            pending_amount = move.amount_residual

            assigned_risk = 'none'
            # Las reglas ya están ordenadas por days_overdue desc, amount_min desc
            for rule in rules:
                if days_overdue >= rule.days_overdue and pending_amount >= rule.amount_min:
                    assigned_risk = rule.risk_level
                    break
            
            move.risk_level = assigned_risk

    @api.model
    def cron_evaluate_collection_risk(self):
        """
        Ejecutado por el Cron para reevaluar el riesgo de todas las facturas abiertas.
        Forzamos el recálculo marcando el campo para actualizar en aquellas facturas que aplican.
        """
        open_invoices = self.search([
            ('move_type', 'in', ('out_invoice', 'out_receipt')),
            ('state', '=', 'posted'),
            ('payment_state', 'not in', ('paid', 'in_payment'))
        ])
        
        # Al modificar la caché o forzar el _compute, se actualiza en base de datos gracias al store=True
        open_invoices._compute_collection_risk()
