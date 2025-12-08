# -*- coding: utf-8 -*-
{
    'name': "HR Phone Extension Management",

    'summary': """
        Add centralized management of internal phone extensions with employee integration
    """,

    'description': """
        HR Phone Extension Management

        This module provides:

        * Centralized phone extension management
        * Bi-directional linking between extensions and employees
        * Integration with employee profiles
        * Menu and views for extension management
        * Ready for future VOIP integration
    """,

    'author': "Technology Pill Business Solution",
    'maintainer': "Technology Pill Business Solution",
    'website': "https://www.tecpill.com/",
    'support': "admin@tecpill.com",

    'category': "Human Resources",
    'version': "19.0.1.0.0",
    'license': "OPL-1",
    'price': 0.00,
    'currency': "USD",

    'images': ['static/description/banner.png'],

    # any module necessary for this one to work correctly
    'depends': [
            "base",
            "hr",
            "mail",
        ],

    # always loaded
    'data': [
            "security/ir.model.access.csv",
            "views/phone_extension_views.xml",
            "views/hr_employee_views.xml",
            "views/hr_employee_public_views.xml",
            "views/phone_extension_menus.xml",
        ],

    'application': True,
    'installable': True,
    'auto_install': False,
}

