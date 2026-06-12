# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo import fields


class TestFiscalRetention(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestFiscalRetention, cls).setUpClass()

        # --- Impuestos ---
        cls.iva_tax = cls.env['account.tax'].create({
            'name': 'IVA 16% Test',
            'amount': 16.0,
            'amount_type': 'percent',
            'type_tax_use': 'sale',
            'company_id': cls.env.company.id,
        })
        cls.retention_tax = cls.env['account.tax'].create({
            'name': 'Retención IVA 75% Test',
            'amount': -12.0,
            'amount_type': 'percent',
            'type_tax_use': 'sale',
            'company_id': cls.env.company.id,
        })

        # --- Posición Fiscal ---
        cls.fiscal_position = cls.env['account.fiscal.position'].create({
            'name': 'Agente de Retención Test',
        })

        # --- Regla de Retención ---
        cls.retention_rule = cls.env['account.retention.rule'].create({
            'name': 'Regla Ret. 75% Test',
            'fiscal_position_id': cls.fiscal_position.id,
            'tax_ids': [(6, 0, [cls.retention_tax.id])],
            'min_amount': 0.0,
        })

        # --- Partner CON posición fiscal ---
        cls.partner_with_fp = cls.env['res.partner'].create({
            'name': 'Cliente Agente Retención',
            'property_account_position_id': cls.fiscal_position.id,
        })

        # --- Partner SIN posición fiscal ---
        cls.partner_without_fp = cls.env['res.partner'].create({
            'name': 'Cliente Sin Posición',
        })

        # --- Producto ---
        cls.product = cls.env['product.product'].create({
            'name': 'Producto Test Retención',
            'list_price': 100.0,
        })

        # --- Cuenta de ingresos ---
        cls.income_account = cls.env['account.account'].search([
            ('account_type', '=', 'income'),
            ('company_id', '=', cls.env.company.id),
        ], limit=1)

    # ---------------------------------------------------------------
    # Caso 1: Factura CON posición fiscal → retención aplicada
    # ---------------------------------------------------------------
    def test_01_retention_applied_on_confirm(self):
        """Al confirmar una factura de un agente de retención, se debe añadir el impuesto de retención."""
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_with_fp.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'price_unit': 100.0,
                'tax_ids': [(6, 0, [self.iva_tax.id])],
                'account_id': self.income_account.id,
            })],
        })
        invoice.action_post()

        line = invoice.invoice_line_ids[0]
        tax_ids = line.tax_ids.ids
        self.assertIn(self.iva_tax.id, tax_ids,
                      "El IVA 16% debe seguir presente en la línea.")
        self.assertIn(self.retention_tax.id, tax_ids,
                      "La retención debe haberse añadido automáticamente al confirmar.")

    # ---------------------------------------------------------------
    # Caso 2: Factura SIN posición fiscal → sin retención
    # ---------------------------------------------------------------
    def test_02_no_retention_without_fiscal_position(self):
        """Si el cliente no tiene posición fiscal, no se aplica ninguna retención."""
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_without_fp.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'price_unit': 100.0,
                'tax_ids': [(6, 0, [self.iva_tax.id])],
                'account_id': self.income_account.id,
            })],
        })
        invoice.action_post()

        line = invoice.invoice_line_ids[0]
        self.assertNotIn(self.retention_tax.id, line.tax_ids.ids,
                         "No debe aplicarse retención sin posición fiscal.")

    # ---------------------------------------------------------------
    # Caso 3: Factura debajo del monto mínimo → sin retención
    # ---------------------------------------------------------------
    def test_03_no_retention_below_min_amount(self):
        """Si la factura no alcanza el monto mínimo de la regla, no se aplica retención."""
        # Actualizar regla con monto mínimo alto
        self.retention_rule.write({'min_amount': 500.0})

        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_with_fp.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'price_unit': 100.0,  # Base 100 < min_amount 500
                'tax_ids': [(6, 0, [self.iva_tax.id])],
                'account_id': self.income_account.id,
            })],
        })
        invoice.action_post()

        line = invoice.invoice_line_ids[0]
        self.assertNotIn(self.retention_tax.id, line.tax_ids.ids,
                         "No debe aplicarse retención si la base es menor al monto mínimo.")

        # Restaurar regla
        self.retention_rule.write({'min_amount': 0.0})

    # ---------------------------------------------------------------
    # Caso 4: Posición fiscal sin regla asociada → sin retención
    # ---------------------------------------------------------------
    def test_04_no_retention_when_no_rule_for_position(self):
        """Si la posición fiscal no tiene regla de retención configurada, no se aplica."""
        fp_sin_regla = self.env['account.fiscal.position'].create({
            'name': 'Posición Exento Test',
        })
        partner = self.env['res.partner'].create({
            'name': 'Cliente Exento',
            'property_account_position_id': fp_sin_regla.id,
        })

        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'price_unit': 100.0,
                'tax_ids': [(6, 0, [self.iva_tax.id])],
                'account_id': self.income_account.id,
            })],
        })
        invoice.action_post()

        line = invoice.invoice_line_ids[0]
        self.assertNotIn(self.retention_tax.id, line.tax_ids.ids,
                         "No debe aplicarse retención si no existe regla para esa posición fiscal.")
