# -*- coding: utf-8 -*-
{
    'name': "User Sign Profile",

    'summary': "Allow internal users to set and update their own digital signatures",

    'description': """
    User Sign Profile

    This module extends the Sign app to allow internal users (base.group_user) to 
    set and update their own digital signatures and initials from their user profile.

    Features:
    * Dual-location access: Signatures accessible in both admin user forms and "My Profile" preferences
    * Users can upload/update their own signature and initials
    * Security restrictions ensure users can only edit their own signatures
    * Context-based protection prevents mixing signature updates with other field changes
    * Admins retain full access to all user signatures
    * Normal preference updates are not affected
    """,

    'author': "Technology Pill Business Solution, Sayed Mohammed Aqeel Ebrahim",
    'maintainer': "Sayed Mohammed Aqeel Ebrahim",
    'website': "https://sayedmohd.com/",

    'category': "Uncategorized",
    'version': "19.0.1.0.0",
    'license': "LGPL-3",
    'images': ['static/description/banner.png'],

    'depends': [
            "base",
            "sign",
        ],

    'data': [
            "views/res_users_sign_profile.xml",
        ],

    'application': False,
    'installable': True,
    'auto_install': False,
}



