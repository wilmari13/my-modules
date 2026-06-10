from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    operation_tag_ids = fields.Many2many(
        'stock.operation.tag',
        string='Etiquetas Operativas',
    )
