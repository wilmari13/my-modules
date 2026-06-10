from odoo import models, fields, api, _

class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = ['product.template', 'mail.thread']

    replenishment_priority = fields.Selection([
        ('low', 'Baja'),
        ('id_medium', 'Media'),
        ('high', 'Alta')
    ], string='Prioridad de Reabastecimiento', default='low')
    
    target_stock = fields.Float(string='Stock Objetivo', default=0.0)


    x_is_critical = fields.Boolean(
        string="Estado Crítico", 
        compute="_compute_is_critical", 
        store=True # Importante para poder agrupar en vistas
    )
    
    @api.depends('qty_available', 'target_stock')
    def _compute_is_critical(self):
        for product in self:
            if product.target_stock > 0:
                product.x_is_critical = product.qty_available < product.target_stock
            else:
                product.x_is_critical = False

    
    @api.model
    def cron_check_replenishment_needs(self):
        """
        Método ejecutado por el Cron para identificar productos desabastecidos
        y generar actividades de alerta sin duplicados.
        """
        # 1. Buscamos productos con stock objetivo configurado
        tracked_products = self.search([('target_stock', '>', 0)])

        # 2. Filtramos los que están por debajo del objetivo
        products_to_replenish = tracked_products.filtered(
            lambda p: p.qty_available < p.target_stock
        )

        activity_type = self.env.ref('mail.activity_type_todo', raise_if_not_found=False)
        if not activity_type:
            activity_type = self.env['mail.activity.type'].search([], limit=1)

        for product in products_to_replenish:
            responsible_user = product.responsible_id.id or self.env.user.id

            # CRITERIO DE ACEPTACIÓN: Evitar duplicados innecesarios [cite: 50]
            existing_activity = self.env['mail.activity'].search([
                ('res_model', '=', 'product.template'),
                ('res_id', '=', product.id),
                ('activity_type_id', '=', activity_type.id),
                ('user_id', '=', responsible_user)
            ], limit=1)

            if existing_activity:
                continue

            # Crear la actividad (mail.activity) [cite: 48]
            self.env['mail.activity'].create({
                'res_model_id': self.env['ir.model']._get('product.template').id,
                'res_id': product.id,
                'activity_type_id': activity_type.id,
                'summary': _('Se debe reabastecer el producto: %s') % product.name,
                'note': _('El stock actual está por debajo del stock objetivo.'),
                'user_id': responsible_user,
            })