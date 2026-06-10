from odoo.tests.common import TransactionCase
from datetime import timedelta
from odoo import fields

class TestCollectionRisk(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestCollectionRisk, cls).setUpClass()
        cls.Rule = cls.env['account.collection.alert.rule']
        cls.Move = cls.env['account.move']
        cls.Partner = cls.env['res.partner'].create({'name': 'Cliente Test Riesgo'})
        
        # Configurar cuenta de ingresos
        cls.income_account = cls.env['account.account'].search([
            ('account_type', '=', 'income'),
            ('company_id', '=', cls.env.company.id)
        ], limit=1)

        # Regla 1: Riesgo Alto (> 30 días, > $500)
        cls.rule_high = cls.Rule.create({
            'name': 'Alto Riesgo',
            'days_overdue': 30,
            'amount_min': 500.0,
            'risk_level': 'high'
        })
        
        # Regla 2: Riesgo Medio (> 15 días, > $100)
        cls.rule_medium = cls.Rule.create({
            'name': 'Medio Riesgo',
            'days_overdue': 15,
            'amount_min': 100.0,
            'risk_level': 'medium'
        })

    def _create_invoice(self, amount, date_due):
        invoice = self.Move.create({
            'move_type': 'out_invoice',
            'partner_id': self.Partner.id,
            'invoice_date': fields.Date.today() - timedelta(days=60), # emitimos hace 60 días
            'invoice_date_due': date_due,
            'invoice_line_ids': [
                (0, 0, {
                    'name': 'Producto Test',
                    'quantity': 1,
                    'price_unit': amount,
                    'account_id': self.income_account.id,
                })
            ]
        })
        invoice.action_post()
        return invoice

    def test_01_high_risk_invoice(self):
        """Factura vencida hace 40 días con monto 1000"""
        due_date = fields.Date.today() - timedelta(days=40)
        invoice = self._create_invoice(1000.0, due_date)
        
        # Odoo reevalúa en acción cron, forcemos el compute
        invoice._compute_collection_risk()
        
        self.assertEqual(invoice.x_risk_level, 'high', "Debería ser Alto Riesgo (>30 días y >500).")

    def test_02_medium_risk_invoice(self):
        """Factura vencida hace 20 días con monto 200"""
        due_date = fields.Date.today() - timedelta(days=20)
        invoice = self._create_invoice(200.0, due_date)
        
        invoice._compute_collection_risk()
        
        self.assertEqual(invoice.x_risk_level, 'medium', "Debería ser Medio Riesgo (>15 días y >100).")

    def test_03_no_risk_invoice(self):
        """Factura vencida hace 10 días (no cae en ninguna regla)"""
        due_date = fields.Date.today() - timedelta(days=10)
        invoice = self._create_invoice(500.0, due_date)
        
        invoice._compute_collection_risk()
        
        self.assertEqual(invoice.x_risk_level, 'none', "No debería tener riesgo asignado.")
