# -*- coding: utf-8 -*-
{
    'name': "Contact Search by Phone",
    'summary': """Search contacts by phone number with smart normalization""",
    'description': """
        Contact Search by Phone Number
        ===============================
        
        Search for contacts using phone or mobile numbers with automatic normalization.
        Supports partial searches and handles different phone formats automatically.
        
        Features:
        ---------
        * Smart phone number normalization (removes spaces, dashes, parentheses)
        * Fast search by full or partial phone number
        * Prefix and suffix search support
        * PostgreSQL indexes for optimal performance
        * Optional phone uniqueness enforcement
        * Cross-field uniqueness (phone vs mobile)
        * Configurable settings in General Settings
    """,
    'author': "TecPill Business Solutions",
    'maintainer': "Sayed Ameen",
    'website': "https://www.tecpill.com",
    'category': 'Contact Management',
    'version': '17.0.2.0.4',
    'license': 'LGPL-3',
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
    ],
    'depends': ['contacts', 'sale'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
