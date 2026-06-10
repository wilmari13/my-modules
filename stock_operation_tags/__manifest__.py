{
    'name': "Stock Operation Tags",
    'summary': "Clasificación operativa de productos con etiquetas",
    'description': """
        Permite clasificar productos con etiquetas operativas (stock.operation.tag)
        para optimizar picking, almacenamiento y despacho.
        Incluye vista Kanban agrupada y wizard de asignación rápida.
    """,
    'author': "Wilmari Padrino",
    'description': """\n        Este módulo permite asignar etiquetas operativas a los productos para mejorar la gestión de picking, almacenamiento y despacho.\n        Proporciona vistas Kanban y un wizard de asignación rápida.\n    """,
    'version': '19.0.1.0.0',
    'depends': ['stock', 'product'],
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
