from odoo import models, fields


class StockOperationTag(models.Model):
    _name = 'stock.operation.tag'
    _description = 'Etiqueta Operativa de Inventario'

    name = fields.Char(string='Nombre', required=True)
    color = fields.Integer(string='Color')
    description = fields.Text(string='Descripción')
    operation_type = fields.Selection([
        ('picking', 'Picking'),
        ('storage', 'Almacenamiento'),
        ('dispatch', 'Despacho'),
    ], string='Tipo de Operación', required=True, default='picking')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'El nombre de la etiqueta debe ser único.'),
    ]
