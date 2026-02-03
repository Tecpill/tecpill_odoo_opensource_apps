# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)

def post_init_hook(env):
    """
    Post-installation hook: Check for duplicate numbers and warn user
    """
    cr = env.cr
    
    _logger.info("=" * 80)
    _logger.info("Contact Search by Phone: Post-Installation Check")
    _logger.info("=" * 80)
    
    # Set default configuration parameters if not already set
    IrConfigParam = env['ir.config_parameter'].sudo()
    
    # Ensure show_phone_in_search is enabled by default
    if not IrConfigParam.get_param('contact_search_by_phone.show_phone_in_search'):
        IrConfigParam.set_param('contact_search_by_phone.show_phone_in_search', 'True')
        _logger.info("✅ Enabled 'Show Phone in Search' by default")
    
    # Ensure enforce_unique is enabled by default
    if not IrConfigParam.get_param('contact_search_by_phone.enforce_unique'):
        IrConfigParam.set_param('contact_search_by_phone.enforce_unique', 'True')
        _logger.info("✅ Enabled 'Enforce Unique Phone Numbers' by default")
    
    # Ensure strip_leading_zero is enabled by default
    if not IrConfigParam.get_param('contact_search_by_phone.strip_leading_zero'):
        IrConfigParam.set_param('contact_search_by_phone.strip_leading_zero', 'True')
        _logger.info("✅ Enabled 'Strip Leading Zero' by default")
    
    # Set minimum digits for search
    if not IrConfigParam.get_param('contact_search_by_phone.min_digits_for_search'):
        IrConfigParam.set_param('contact_search_by_phone.min_digits_for_search', '3')
        _logger.info("✅ Set 'Minimum Digits for Search' to 3")
    
    # Check for duplicate numbers in phone_clean
    cr.execute("""
        SELECT phone_clean, COUNT(*) as count, array_agg(id) as partner_ids
        FROM res_partner
        WHERE phone_clean IS NOT NULL AND phone_clean <> ''
        GROUP BY phone_clean
        HAVING COUNT(*) > 1
    """)
    
    phone_duplicates = cr.fetchall()
    
    if phone_duplicates:
        _logger.warning("⚠️  Found %s duplicate phone numbers:", len(phone_duplicates))
        for phone, count, ids in phone_duplicates[:5]:  # Show first 5 only
            partners = env['res.partner'].browse(ids)
            names = ', '.join(partners.mapped('name')[:3])
            _logger.warning("  • Phone: %s (Used by %s contacts: %s...)", phone, count, names)
        
        if len(phone_duplicates) > 5:
            _logger.warning("  ... and %s more duplicate phone numbers", len(phone_duplicates) - 5)
    
    # Check for duplicate numbers in mobile_clean
    cr.execute("""
        SELECT mobile_clean, COUNT(*) as count, array_agg(id) as partner_ids
        FROM res_partner
        WHERE mobile_clean IS NOT NULL AND mobile_clean <> ''
        GROUP BY mobile_clean
        HAVING COUNT(*) > 1
    """)
    
    mobile_duplicates = cr.fetchall()
    
    if mobile_duplicates:
        _logger.warning("⚠️  Found %s duplicate mobile numbers:", len(mobile_duplicates))
        for mobile, count, ids in mobile_duplicates[:5]:
            partners = env['res.partner'].browse(ids)
            names = ', '.join(partners.mapped('name')[:3])
            _logger.warning("  • Mobile: %s (Used by %s contacts: %s...)", mobile, count, names)
        
        if len(mobile_duplicates) > 5:
            _logger.warning("  ... and %s more duplicate mobile numbers", len(mobile_duplicates) - 5)
    
    # Check for cross-field duplicates (phone_clean vs mobile_clean)
    cr.execute("""
        WITH nums AS (
          SELECT id, phone_clean AS num FROM res_partner
          WHERE phone_clean IS NOT NULL AND phone_clean <> ''
          UNION ALL
          SELECT id, mobile_clean AS num FROM res_partner
          WHERE mobile_clean IS NOT NULL AND mobile_clean <> ''
        )
        SELECT num, COUNT(*) AS cnt, array_agg(id) AS partner_ids
        FROM nums
        GROUP BY num
        HAVING COUNT(*) > 1
    """)
    
    cross_field_duplicates = cr.fetchall()
    
    if cross_field_duplicates:
        _logger.warning("⚠️  Found %s cross-field duplicates (phone vs mobile):", len(cross_field_duplicates))
        for num, count, ids in cross_field_duplicates[:5]:
            # Remove duplicates from ids list (same partner might have both fields)
            unique_ids = list(set(ids))
            partners = env['res.partner'].browse(unique_ids)
            names = ', '.join(partners.mapped('name')[:3])
            _logger.warning("  • Number: %s (Used in %s fields across contacts: %s...)", num, count, names)
        
        if len(cross_field_duplicates) > 5:
            _logger.warning("  ... and %s more cross-field duplicates", len(cross_field_duplicates) - 5)
    
    if phone_duplicates or mobile_duplicates or cross_field_duplicates:
        _logger.warning("=" * 80)
        _logger.warning("⚠️  ACTION REQUIRED:")
        _logger.warning("Please clean duplicate phone/mobile numbers before they cause issues.")
        _logger.warning("You can temporarily disable uniqueness check by setting:")
        _logger.warning("Settings → General Settings → Contact Phone Search → Enforce Unique Phone Numbers = OFF")
        _logger.warning("=" * 80)
    else:
        _logger.info("✅ No duplicate phone numbers found. All good!")
        _logger.info("=" * 80)

def uninstall_hook(env):
    """
    Uninstall hook: Cleanup
    """
    _logger.info("Contact Search by Phone: Uninstalling...")
