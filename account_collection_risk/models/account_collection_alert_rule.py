from odoo import models, fields

class AccountCollectionAlertRule(models.Model):
    _name = 'account.collection.alert.rule'
    _description = 'Collection Risk Alert Rule'
    _order = 'days_overdue desc, amount_min desc'

    name = fields.Char(string='Nombre de la Regla', required=True)
    days_overdue = fields.Integer(string='Días Mínimos de Atraso', required=True, default=0)
    amount_min = fields.Float(string='Monto Mínimo Pendiente', required=True, default=0.0)
    risk_level = fields.Selection([
        ('low', 'Bajo'),
        ('medium', 'Medio'),
        ('high', 'Alto')
    ], string='Nivel de Riesgo', required=True, default='low')
