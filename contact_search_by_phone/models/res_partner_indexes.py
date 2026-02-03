# -*- coding: utf-8 -*-

from odoo import api, models
import logging

_logger = logging.getLogger(__name__)

class ResPartnerIndexes(models.Model):
    """
    Additional model to create optimized PostgreSQL indexes
    """
    _inherit = 'res.partner'

    def init(self):
        """
        Create custom PostgreSQL indexes for optimal performance
        Executed when installing/updating the module
        """
        super().init()
        
        # text_pattern_ops index for phone_clean (for LIKE 'xxx%' search)
        self._cr.execute("""
            CREATE INDEX IF NOT EXISTS res_partner_phone_clean_pattern_idx
            ON res_partner (phone_clean text_pattern_ops)
            WHERE phone_clean IS NOT NULL AND phone_clean <> '';
        """)
        
        # text_pattern_ops index for mobile_clean (for LIKE 'xxx%' search)
        self._cr.execute("""
            CREATE INDEX IF NOT EXISTS res_partner_mobile_clean_pattern_idx
            ON res_partner (mobile_clean text_pattern_ops)
            WHERE mobile_clean IS NOT NULL AND mobile_clean <> '';
        """)
        
        # text_pattern_ops index for phone_clean_rev (for Ends-with search)
        self._cr.execute("""
            CREATE INDEX IF NOT EXISTS res_partner_phone_clean_rev_pattern_idx
            ON res_partner (phone_clean_rev text_pattern_ops)
            WHERE phone_clean_rev IS NOT NULL AND phone_clean_rev <> '';
        """)
        
        # text_pattern_ops index for mobile_clean_rev (for Ends-with search)
        self._cr.execute("""
            CREATE INDEX IF NOT EXISTS res_partner_mobile_clean_rev_pattern_idx
            ON res_partner (mobile_clean_rev text_pattern_ops)
            WHERE mobile_clean_rev IS NOT NULL AND mobile_clean_rev <> '';
        """)
        
        _logger.info("✅ Custom PostgreSQL indexes created successfully for phone search optimization (including reverse fields)")
