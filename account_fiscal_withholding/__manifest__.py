# -*- coding: utf-8 -*-
{
    'name': "Account Fiscal Withholding",
    'summary': "Aplicar retenciones automáticas en facturas",
    'description': """
        Aplica retenciones automáticas basadas en la posición fiscal de la factura.
    """,
    'author': "Wilmari Padrino",
    'category': 'Accounting/Accounting',
    'version': '19.0.1.0.0',
    'depends': ['account'],
    'data': [
        'data/account_tax_data.xml',
        'data/account_fiscal_position_data.xml',
        'security/ir.model.access.csv',
        'views/account_retention_rule_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
