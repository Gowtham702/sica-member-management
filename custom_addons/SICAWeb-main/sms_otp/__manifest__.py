# -*- coding: utf-8 -*-
{
    'name': 'SICA - OTP Sms ',
    'version': '1.0',
    'category': 'sica',
    'summary': 'SICA - Otp Management',
    'description': 'SICA - Otp Management',
    'author': 'Muthaiyan',
    'depends': ['member_management_system'],
    'data': [
        'security/ir.model.access.csv',
        'views/sms_otp.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': True,
}
