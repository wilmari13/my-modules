{
    'name': "Account Collection Risk",
    'summary': "Identify invoices with high collection risk using an automated dashboard",
    'description': """
        This module evaluates overdue invoices automatically based on rules
        (days overdue and minimum amount) and classifies them by risk level.
        It provides a Kanban dashboard to monitor high-risk invoices.
    """,
    'author': "Wilmari Padrino",
    'category': 'Accounting/Accounting',
    'version': '19.0.1.0.0',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/account_collection_alert_rule_views.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
