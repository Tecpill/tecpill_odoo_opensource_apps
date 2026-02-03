# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    min_digits_for_phone_search = fields.Integer(
        string='Minimum Digits for Phone Search',
        default=3,
        config_parameter='contact_search_by_phone.min_digits_for_search',
        help="Minimum number of digits required to trigger phone number search (default: 3)"
    )
    
    enforce_unique_phones = fields.Boolean(
        string='Enforce Unique Phone Numbers',
        default=True,
        config_parameter='contact_search_by_phone.enforce_unique',
        help="Prevent creating/updating contacts with duplicate phone numbers"
    )
    
    show_phone_in_search = fields.Boolean(
        string='Show Phone in Search Results',
        default=True,
        config_parameter='contact_search_by_phone.show_phone_in_search',
        help="Display phone number alongside name in search results (e.g., 'John Doe — 0551234567')"
    )
    
    strip_leading_zero = fields.Boolean(
        string='Strip Leading Zero from Phone Numbers',
        default=True,
        config_parameter='contact_search_by_phone.strip_leading_zero',
        help="If enabled: 0551234567 → 551234567. If disabled: keep leading zero. "
             "Note: '00' international prefix is always removed (e.g., 00966 → 966)."
    )
