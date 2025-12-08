# -*- coding: utf-8 -*-
{
    'name': "Logging Cleanup",

    'summary': """
    Configurable log retention policies, cleanup rotation modes, and manual cleanup for ir.logging
    """,

    'description': """
    Logging Cleanup Module

    This module enhances Odoo's built-in ir.logging model with:

    * Configurable log retention policies per log level
    * Time-based and count-based rotation modes
    * Automated scheduled cleanup via cron job
    * Manual cleanup button in settings and log list view
    * Optimized SQL-based cleanup for large tables
    * Audit logging after each cleanup operation
    """,

    'author': "Technology Pill Business Solution, Sayed Mohammed Aqeel Ebrahim",
    'maintainer': "Sayed Mohammed Aqeel Ebrahim",
    'website': "https://tecpill.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': "Technical",
    'version': "16.0.1.0.0",
    'license': "LGPL-3",

    # any module necessary for this one to work correctly
    'depends': [
            "base",
            "base_setup",
        ],

    # always loaded
    'data': [
            "security/ir.model.access.csv",
            "data/ir_cron_data.xml",
            "views/res_config_settings_views.xml",
            "views/ir_logging_views.xml",
        ],

    'application': True,
    'installable': True,
    'auto_install': False,
}


