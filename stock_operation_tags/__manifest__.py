{
    'name': "Stock Operation Tags",
    'summary': "Clasificación operativa de productos con etiquetas",
    'description': """
        Permite clasificar productos con etiquetas operativas (stock.operation.tag)
        para optimizar picking, almacenamiento y despacho.
        Incluye vista Kanban agrupada y wizard de asignación rápida.
    """,
    'author': "Your Company",
    'category': 'Inventory/Inventory',
    'version': '19.0.1.0.0',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/product_tag_assign_wizard_views.xml',
        'views/stock_operation_tag_views.xml',
        'views/product_template_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
