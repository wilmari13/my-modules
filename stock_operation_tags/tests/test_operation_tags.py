# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestStockOperationTags(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestStockOperationTags, cls).setUpClass()

        cls.Tag = cls.env['stock.operation.tag']
        cls.ProductTemplate = cls.env['product.template']

        # Crear etiquetas operativas
        cls.tag_picking = cls.Tag.create({
            'name': 'Zona Picking A',
            'color': 1,
            'description': 'Productos de alta rotación',
            'operation_type': 'picking',
        })
        cls.tag_storage = cls.Tag.create({
            'name': 'Almacén Frío',
            'color': 2,
            'description': 'Productos refrigerados',
            'operation_type': 'storage',
        })
        cls.tag_dispatch = cls.Tag.create({
            'name': 'Despacho Express',
            'color': 3,
            'description': 'Envío prioritario',
            'operation_type': 'dispatch',
        })

        # Producto de prueba
        cls.product = cls.ProductTemplate.create({
            'name': 'Producto Test Tags',
            'type': 'product',
        })

    # ---------------------------------------------------------------
    # Caso 1: Creación correcta de etiquetas
    # ---------------------------------------------------------------
    def test_01_tag_creation(self):
        """Verificar que las etiquetas se crean correctamente con todos sus campos."""
        self.assertEqual(self.tag_picking.name, 'Zona Picking A')
        self.assertEqual(self.tag_picking.operation_type, 'picking')
        self.assertEqual(self.tag_storage.operation_type, 'storage')
        self.assertEqual(self.tag_dispatch.operation_type, 'dispatch')
        self.assertTrue(self.tag_picking.id, "La etiqueta debe tener un ID asignado.")

    # ---------------------------------------------------------------
    # Caso 2: Unicidad del nombre (SQL constraint)
    # ---------------------------------------------------------------
    def test_02_tag_name_unique(self):
        """No se deben crear dos etiquetas con el mismo nombre."""
        from psycopg2 import IntegrityError
        with self.assertRaises(IntegrityError):
            self.Tag.create({
                'name': 'Zona Picking A',  # Duplicado
                'operation_type': 'picking',
            })

    # ---------------------------------------------------------------
    # Caso 3: Asignación Many2many a productos
    # ---------------------------------------------------------------
    def test_03_assign_tags_to_product(self):
        """Verificar que se pueden asignar etiquetas a un producto."""
        self.product.write({
            'operation_tag_ids': [(6, 0, [self.tag_picking.id, self.tag_storage.id])],
        })
        self.assertEqual(len(self.product.operation_tag_ids), 2,
                         "El producto debe tener 2 etiquetas asignadas.")
        self.assertIn(self.tag_picking, self.product.operation_tag_ids)
        self.assertIn(self.tag_storage, self.product.operation_tag_ids)

    # ---------------------------------------------------------------
    # Caso 4: Remover etiquetas de un producto
    # ---------------------------------------------------------------
    def test_04_remove_tag_from_product(self):
        """Verificar que se pueden quitar etiquetas de un producto."""
        self.product.write({
            'operation_tag_ids': [(6, 0, [self.tag_picking.id, self.tag_storage.id])],
        })
        # Quitar una etiqueta
        self.product.write({
            'operation_tag_ids': [(3, self.tag_storage.id)],
        })
        self.assertEqual(len(self.product.operation_tag_ids), 1,
                         "El producto debe tener solo 1 etiqueta después de la remoción.")
        self.assertNotIn(self.tag_storage, self.product.operation_tag_ids)

    # ---------------------------------------------------------------
    # Caso 5: Wizard de asignación rápida
    # ---------------------------------------------------------------
    def test_05_wizard_assign_tags(self):
        """El wizard debe poder asignar etiquetas a un producto."""
        Wizard = self.env['product.tag.assign.wizard']
        wizard = Wizard.with_context(
            active_ids=[self.product.id],
            active_model='product.template',
        ).create({
            'tag_ids': [(6, 0, [self.tag_dispatch.id])],
        })
        wizard.action_apply()

        self.assertIn(self.tag_dispatch, self.product.operation_tag_ids,
                      "El wizard debe asignar la etiqueta al producto.")

    # ---------------------------------------------------------------
    # Caso 6: Wizard reemplaza las etiquetas existentes
    # ---------------------------------------------------------------
    def test_06_wizard_replaces_tags(self):
        """El wizard reemplaza las etiquetas existentes del producto."""
        # Asignar etiqueta inicial
        self.product.write({
            'operation_tag_ids': [(6, 0, [self.tag_picking.id])],
        })
        self.assertEqual(len(self.product.operation_tag_ids), 1)

        # Usar wizard para reemplazar con otra etiqueta
        Wizard = self.env['product.tag.assign.wizard']
        wizard = Wizard.with_context(
            active_ids=[self.product.id],
            active_model='product.template',
        ).create({
            'tag_ids': [(6, 0, [self.tag_storage.id, self.tag_dispatch.id])],
        })
        wizard.action_apply()

        self.assertEqual(len(self.product.operation_tag_ids), 2,
                         "El wizard debe reemplazar las etiquetas con las nuevas seleccionadas.")
        self.assertNotIn(self.tag_picking, self.product.operation_tag_ids,
                         "La etiqueta original no debe estar después del reemplazo.")
