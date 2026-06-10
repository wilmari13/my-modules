from odoo.tests.common import TransactionCase


class TestReplenishmentPriorityExtra(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductTemplate = cls.env['product.template']
        cls.Activity = cls.env['mail.activity']
        # Ensure activity type exists
        cls.activity_type = cls.env.ref('mail.activity_type_todo', raise_if_not_found=False)
        if not cls.activity_type:
            cls.activity_type = cls.env['mail.activity.type'].create({'name': 'To Do'})
        # Producto con stock objetivo negativo
        cls.product_negative = cls.ProductTemplate.create({
            'name': 'Producto Negativo',
            'type': 'product',
            'replenishment_priority': 'low',
            'target_stock': -5.0,
        })

    def test_negative_target_stock_no_activity(self):
        """Cuando el target_stock es negativo, no debe crearse actividad"""
        # Ejecutamos el cron
        self.ProductTemplate.cron_check_replenishment_needs()
        activities = self.Activity.search([
            ('res_model', '=', 'product.template'),
            ('res_id', '=', self.product_negative.id),
        ])
        self.assertEqual(len(activities), 0, "No debe generarse actividad para stock objetivo negativo")
