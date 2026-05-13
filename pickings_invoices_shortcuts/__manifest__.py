# -*- coding: utf-8 -*-
{
    'name': "Pickings Invoices Shortcuts",

    'summary': "Add missing smart button navigation: Picking↔Invoice links",

    'description': """
Smart Button Navigation Enhancement
===================================
This module adds only the truly missing smart button navigation:

✅ EXISTING (preserved):
- Sale Order → Invoices (smart button)
- Sale Order → Deliveries (smart button)  
- Stock Picking → Sale Order (regular field)
- Invoice → Sale Order (smart button) ← Already exists!

🆕 ADDED (what's actually missing):
- Stock Picking → Sale Order (smart button upgrade)
- Stock Picking → Invoices (smart button) 
- Invoice → Pickings (smart button)

Scope: Only 3 missing smart buttons, leveraging existing sale_stock relationships.
    """,

    'author': 'Technology Pill Business Solution, Sayed Mohammed Aqeel Ebrahim',
    'website': "https://www.Tecpill.com",
    'license': 'LGPL-3',

    'category': 'Sales/Stock/Accounting',
    'version': '17.0.1.0.0',

    # Dependencies - including sale_stock for existing functionality
    'depends': ['sale_stock'],  # This already includes base, sale, stock, account

    'images': [
    'static/description/banner.png',
    ], 

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml', 
        'views/account_move_views.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': False,
}

