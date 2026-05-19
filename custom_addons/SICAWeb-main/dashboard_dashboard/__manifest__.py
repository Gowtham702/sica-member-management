# -*- coding: utf-8 -*-
{
    'name': 'SICA_dashboard',
    'version': '15.0',
    "author": "By Manoj",
    'summary': 'SICA Customization',
    'description': """
        Add Additional custom field and function added on SICA module.
    """,
    'category': 'Hidden',
    'depends': ['web', 'mail', 'member_management_system'],
    'data': [
        'views/sica_view.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': [
            'dashboard_dashboard/static/src/js/dashboard.js',
            'dashboard_dashboard/static/src/js/on_click.js',
            'dashboard_dashboard/static/src/css/dashboard.css',

        ],
        'web.assets_qweb': [
            'dashboard_dashboard/static/src/xml/dashboard.xml',
            'dashboard_dashboard/static/src/xml/quick_view.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
