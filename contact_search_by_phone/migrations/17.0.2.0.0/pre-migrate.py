# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """
    Migration script to add new reverse fields
    """
    _logger.info("=" * 80)
    _logger.info("Contact Search by Phone: Migration to 17.0.2.0.0")
    _logger.info("=" * 80)
    
    # Add phone_clean_rev column
    cr.execute("""
        ALTER TABLE res_partner 
        ADD COLUMN IF NOT EXISTS phone_clean_rev VARCHAR;
    """)
    _logger.info("✅ Added column: phone_clean_rev")
    
    # Add mobile_clean_rev column
    cr.execute("""
        ALTER TABLE res_partner 
        ADD COLUMN IF NOT EXISTS mobile_clean_rev VARCHAR;
    """)
    _logger.info("✅ Added column: mobile_clean_rev")
    
    # Create basic indexes (pattern indexes will be created by init())
    cr.execute("""
        CREATE INDEX IF NOT EXISTS res_partner_phone_clean_rev_idx 
        ON res_partner (phone_clean_rev) 
        WHERE phone_clean_rev IS NOT NULL AND phone_clean_rev <> '';
    """)
    _logger.info("✅ Created index: res_partner_phone_clean_rev_idx")
    
    cr.execute("""
        CREATE INDEX IF NOT EXISTS res_partner_mobile_clean_rev_idx 
        ON res_partner (mobile_clean_rev) 
        WHERE mobile_clean_rev IS NOT NULL AND mobile_clean_rev <> '';
    """)
    _logger.info("✅ Created index: res_partner_mobile_clean_rev_idx")
    
    _logger.info("=" * 80)
    _logger.info("Migration completed successfully!")
    _logger.info("=" * 80)
