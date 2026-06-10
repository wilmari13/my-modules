from odoo.tests.common import TransactionCase

class TestReplenishmentPriority(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestReplenishmentPriority, cls).setUpClass()
        
        cls.ProductTemplate = cls.env['product.template']
        cls.Activity = cls.env['mail.activity']
        
        # Crear un tipo de actividad si no existe para la prueba
        cls.activity_type = cls.env.ref('mail.activity_type_todo', raise_if_not_found=False)
        if not cls.activity_type:
            cls.activity_type = cls.env['mail.activity.type'].create({
                'name': 'To Do',
            })
            
        # Producto para probar creación y duplicados (Stock actual 0, objetivo 10)
        cls.product_critical = cls.ProductTemplate.create({
            'name': 'Test Product Critical',
            'type': 'product',
            'replenishment_priority': 'high',
            'target_stock': 10.0,
        })
        
        # Producto para probar no creación (Stock objetivo 0)
        cls.product_ok = cls.ProductTemplate.create({
            'name': 'Test Product OK',
            'type': 'product',
            'replenishment_priority': 'low',
            'target_stock': 0.0,
        })

    def test_01_activity_creation_below_target(self):
        """Validar la creación de actividades para productos por debajo del stock objetivo"""
        # Aseguramos que qty_available sea menor que target_stock (por defecto 0 < 10)
        self.assertTrue(self.product_critical.qty_available < self.product_critical.target_stock)
        
        # Ejecutamos el cron
        self.ProductTemplate.cron_check_replenishment_needs()
        
        # Verificamos que se haya creado la actividad
        activities = self.Activity.search([
            ('res_model', '=', 'product.template'),
            ('res_id', '=', self.product_critical.id),
        ])
        
        self.assertEqual(len(activities), 1, "Debe crearse exactamente una actividad.")
        self.assertEqual(activities[0].summary, 'Reabastecimiento Urgente: %s' % self.product_critical.name)

    def test_02_prevent_duplicate_activity(self):
        """Validar que no se creen duplicados innecesarios para el mismo producto"""
        # Ejecutamos el cron por primera vez
        self.ProductTemplate.cron_check_replenishment_needs()
        
        # Ejecutamos el cron por segunda vez
        self.ProductTemplate.cron_check_replenishment_needs()
        
        # Verificamos que solo haya 1 actividad y no 2
        activities = self.Activity.search([
            ('res_model', '=', 'product.template'),
            ('res_id', '=', self.product_critical.id),
        ])
        
        self.assertEqual(len(activities), 1, "No debe crearse una actividad duplicada para el mismo producto.")

    def test_03_no_activity_when_target_not_set(self):
        """Validar que no se creen actividades si el stock objetivo es 0 o menor"""
        self.ProductTemplate.cron_check_replenishment_needs()
        
        activities = self.Activity.search([
            ('res_model', '=', 'product.template'),
            ('res_id', '=', self.product_ok.id),
        ])
        
        self.assertEqual(len(activities), 0, "No debe crearse actividad si el producto no tiene stock objetivo.")
