{
    'name': "Stock Replenishment Priority",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "Wilmari Padrino",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '19.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['stock', 'mail'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/product_template_views.xml',
    ],
    # only loaded in demonstration mode

}

