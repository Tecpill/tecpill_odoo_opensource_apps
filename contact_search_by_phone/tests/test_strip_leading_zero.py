# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


class TestStripLeadingZero(TransactionCase):
    """Tests for strip_leading_zero configuration parameter"""

    def setUp(self):
        super().setUp()
        self.Partner = self.env['res.partner']
        self.Config = self.env['ir.config_parameter'].sudo()

    def test_strip_leading_zero_enabled(self):
        """Test strip_leading_zero when enabled (default behavior)"""
        self.Config.set_param('contact_search_by_phone.strip_leading_zero', 'True')
        p = self.Partner.create({'name': 'P1', 'phone': '0551234567'})
        self.assertEqual(p.phone_clean, '551234567')

    def test_strip_leading_zero_disabled(self):
        """Test strip_leading_zero when disabled - should keep leading zero"""
        self.Config.set_param('contact_search_by_phone.strip_leading_zero', 'False')
        p = self.Partner.create({'name': 'P2', 'phone': '0551234567'})
        self.assertEqual(p.phone_clean, '0551234567')

    def test_always_strip_00_prefix(self):
        """Test that 00 prefix is ALWAYS stripped regardless of setting"""
        self.Config.set_param('contact_search_by_phone.strip_leading_zero', 'False')
        p = self.Partner.create({'name': 'P3', 'phone': '00966551234567'})
        # 00 should be stripped even when strip_leading_zero is False
        self.assertEqual(p.phone_clean, '966551234567')

    def test_strip_leading_zero_mobile_enabled(self):
        """Test strip_leading_zero on mobile field when enabled"""
        self.Config.set_param('contact_search_by_phone.strip_leading_zero', 'True')
        p = self.Partner.create({'name': 'P4', 'mobile': '0559876543'})
        self.assertEqual(p.mobile_clean, '559876543')

    def test_strip_leading_zero_mobile_disabled(self):
        """Test strip_leading_zero on mobile field when disabled"""
        self.Config.set_param('contact_search_by_phone.strip_leading_zero', 'False')
        p = self.Partner.create({'name': 'P5', 'mobile': '0559876543'})
        self.assertEqual(p.mobile_clean, '0559876543')

    def test_search_matches_storage_enabled(self):
        """Test that search uses same normalization as storage (enabled)"""
        self.Config.set_param('contact_search_by_phone.strip_leading_zero', 'True')
        p = self.Partner.create({'name': 'SearchTest1', 'phone': '0551111111'})
        # Storage: 551111111 (stripped)
        # Search should also strip
        results = self.Partner.name_search('0551111111')
        result_ids = [r[0] for r in results]
        self.assertIn(p.id, result_ids, "Search should find partner when both strip")

    def test_search_matches_storage_disabled(self):
        """Test that search uses same normalization as storage (disabled)"""
        self.Config.set_param('contact_search_by_phone.strip_leading_zero', 'False')
        p = self.Partner.create({'name': 'SearchTest2', 'phone': '0552222222'})
        # Storage: 0552222222 (NOT stripped)
        # Search should also NOT strip
        results = self.Partner.name_search('0552222222')
        result_ids = [r[0] for r in results]
        self.assertIn(p.id, result_ids, "Search should find partner when both keep zero")

    def test_no_leading_zero_unaffected(self):
        """Test that numbers without leading zero work in both modes"""
        # Test with setting enabled
        self.Config.set_param('contact_search_by_phone.strip_leading_zero', 'True')
        p1 = self.Partner.create({'name': 'P6', 'phone': '966551234567'})
        self.assertEqual(p1.phone_clean, '966551234567')
        
        # Test with setting disabled
        self.Config.set_param('contact_search_by_phone.strip_leading_zero', 'False')
        p2 = self.Partner.create({'name': 'P7', 'phone': '966559876543'})
        self.assertEqual(p2.phone_clean, '966559876543')

    def test_single_zero_not_stripped_enabled(self):
        """Test that a phone number that is just '0' is not stripped"""
        self.Config.set_param('contact_search_by_phone.strip_leading_zero', 'True')
        p = self.Partner.create({'name': 'P8', 'phone': '0'})
        # Single '0' should remain '0' (len check: len(clean) > 1)
        self.assertEqual(p.phone_clean, '0')

    def test_update_phone_respects_setting(self):
        """Test that updating phone number respects current setting"""
        # Create with setting enabled
        self.Config.set_param('contact_search_by_phone.strip_leading_zero', 'True')
        p = self.Partner.create({'name': 'P9', 'phone': '0553333333'})
        self.assertEqual(p.phone_clean, '553333333')
        
        # Disable setting and update phone
        self.Config.set_param('contact_search_by_phone.strip_leading_zero', 'False')
        p.write({'phone': '0554444444'})
        # Should now keep leading zero
        self.assertEqual(p.phone_clean, '0554444444')
