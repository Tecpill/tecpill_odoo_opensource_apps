# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


class TestPhoneNormalization(TransactionCase):
    """Tests for phone number normalization"""
    
    def setUp(self):
        super().setUp()
        self.Partner = self.env['res.partner']
    
    def test_normalize_simple_phone(self):
        """Test normalizing simple phone number"""
        partner = self.Partner.create({
            'name': 'Test Partner',
            'phone': '0551234567'
        })
        self.assertEqual(partner.phone_clean, '551234567')
    
    def test_normalize_phone_with_spaces(self):
        """Test normalizing phone with spaces"""
        partner = self.Partner.create({
            'name': 'Test Partner',
            'phone': '055 123 4567'
        })
        self.assertEqual(partner.phone_clean, '551234567')
    
    def test_normalize_phone_with_dashes(self):
        """Test normalizing phone with dashes"""
        partner = self.Partner.create({
            'name': 'Test Partner',
            'phone': '055-123-4567'
        })
        self.assertEqual(partner.phone_clean, '551234567')
    
    def test_normalize_phone_with_parentheses(self):
        """Test normalizing phone with parentheses"""
        partner = self.Partner.create({
            'name': 'Test Partner',
            'phone': '(055) 123-4567'
        })
        self.assertEqual(partner.phone_clean, '551234567')
    
    def test_normalize_international_plus(self):
        """Test normalizing international format with +"""
        partner = self.Partner.create({
            'name': 'Test Partner',
            'phone': '+966551234567'
        })
        self.assertEqual(partner.phone_clean, '966551234567')
    
    def test_normalize_international_00(self):
        """Test normalizing international format with 00"""
        partner = self.Partner.create({
            'name': 'Test Partner',
            'phone': '00966551234567'
        })
        self.assertEqual(partner.phone_clean, '966551234567')
    
    def test_normalize_mobile(self):
        """Test normalizing mobile field"""
        partner = self.Partner.create({
            'name': 'Test Partner',
            'mobile': '055-777-8888'
        })
        self.assertEqual(partner.mobile_clean, '557778888')
    
    def test_null_phone_normalization(self):
        """Test NULL phone normalization"""
        partner = self.Partner.create({
            'name': 'Test Partner'
        })
        self.assertFalse(partner.phone_clean)
    
    def test_empty_phone_normalization(self):
        """Test empty phone normalization"""
        partner = self.Partner.create({
            'name': 'Test Partner',
            'phone': ''
        })
        self.assertFalse(partner.phone_clean)
    
    def test_phone_update_renormalize(self):
        """Test re-normalization after phone update"""
        partner = self.Partner.create({
            'name': 'Test Partner',
            'phone': '0551111111'
        })
        self.assertEqual(partner.phone_clean, '551111111')
        
        # Update phone
        partner.write({'phone': '0552222222'})
        self.assertEqual(partner.phone_clean, '552222222')
    
    def test_phone_clean_rev_generation(self):
        """Test reversed phone number generation"""
        partner = self.Partner.create({
            'name': 'Test Partner',
            'phone': '0551234567'
        })
        # Normalized: 551234567, Reversed: 765432155
        self.assertEqual(partner.phone_clean_rev, '765432155')
    
    def test_mobile_clean_rev_generation(self):
        """Test reversed mobile number generation"""
        partner = self.Partner.create({
            'name': 'Test Partner',
            'mobile': '0559876543'
        })
        # Normalized: 559876543, Reversed: 345678955
        self.assertEqual(partner.mobile_clean_rev, '345678955')
    
    def test_strip_leading_zero_enabled(self):
        """Test strip_leading_zero when enabled (default)"""
        # Ensure setting is enabled
        self.env['ir.config_parameter'].sudo().set_param(
            'contact_search_by_phone.strip_leading_zero', 'True'
        )
        
        partner = self.Partner.create({
            'name': 'Test Partner',
            'phone': '0551234567'
        })
        # Should strip leading 0
        self.assertEqual(partner.phone_clean, '551234567')
    
    def test_strip_leading_zero_disabled(self):
        """Test strip_leading_zero when disabled"""
        # Disable the setting
        self.env['ir.config_parameter'].sudo().set_param(
            'contact_search_by_phone.strip_leading_zero', 'False'
        )
        
        partner = self.Partner.create({
            'name': 'Test Partner',
            'phone': '0551234567'
        })
        # Should NOT strip leading 0
        self.assertEqual(partner.phone_clean, '0551234567')
        
        # Reset to default after test
        self.env['ir.config_parameter'].sudo().set_param(
            'contact_search_by_phone.strip_leading_zero', 'True'
        )
    
    def test_strip_leading_zero_not_affect_00_prefix(self):
        """Test that strip_leading_zero doesn't affect 00 international prefix"""
        # Disable strip_leading_zero
        self.env['ir.config_parameter'].sudo().set_param(
            'contact_search_by_phone.strip_leading_zero', 'False'
        )
        
        partner = self.Partner.create({
            'name': 'Test Partner',
            'phone': '00966551234567'
        })
        # Should still strip 00 prefix (always removed)
        self.assertEqual(partner.phone_clean, '966551234567')
        
        # Reset
        self.env['ir.config_parameter'].sudo().set_param(
            'contact_search_by_phone.strip_leading_zero', 'True'
        )
