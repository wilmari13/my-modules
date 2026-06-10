from odoo import models, fields, api

class ProductTagAssignWizard(models.TransientModel):
    _name = 'product.tag.assign.wizard'
    _description = 'Asistente de Asignación Rápida de Etiquetas'

    tag_ids = fields.Many2many('stock.operation.tag', string='Etiquetas')

    @api.model
    def default_get(self, fields_list):
        """Precarga las etiquetas actuales del producto en el Wizard."""
        res = super(ProductTagAssignWizard, self).default_get(fields_list)
        
        active_ids = self.env.context.get('active_ids') or [self.env.context.get('active_id')]
        active_ids = [aid for aid in active_ids if aid]

        if active_ids:
            product = self.env['product.template'].browse(active_ids[0])
            if product.exists() and 'tag_ids' in fields_list:
                # Carga las etiquetas actuales del producto en el modal
                res['tag_ids'] = [(6, 0, product.operation_tag_ids.ids)]
        
        return res

    def action_apply(self):
        """Aplica las etiquetas seleccionadas directamente al producto."""
        active_ids = self.env.context.get('active_ids') or [self.env.context.get('active_id')]
        active_ids = [aid for aid in active_ids if aid]

        if not active_ids:
            return {'type': 'ir.actions.act_window_close'}

        products = self.env['product.template'].browse(active_ids)
        for product in products:
            # Reemplaza el contenido actual por lo seleccionado en el wizard
            product.operation_tag_ids = [(6, 0, self.tag_ids.ids)]

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',  # Recarga la vista Kanban de inmediato
        }
