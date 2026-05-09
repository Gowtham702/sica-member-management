{
    'name': 'SICA Member Management',
    'version': '19.0.1.0.0',
    'summary': 'Manage SICA Members, Memberships and Payments',
    'description': 'A complete module to manage members, membership types for SICA.',
    'author': 'SICA',
    'category': 'Members',
    'depends': ['base', 'mail'],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'data/membership_data.xml',
        'data/sequence_data.xml',
        'views/membership_type_views.xml',
        'views/member_views.xml',
        'views/menu_views.xml',
        'report/member_report.xml',
        'report/member_report_template.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
	'assets': {
        'web.assets_web': [
            'member_management/static/src/css/member_style.css',
        ],
    },
}
