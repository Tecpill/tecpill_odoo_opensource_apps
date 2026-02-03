# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


class TestPhoneSearch(TransactionCase):
    """Tests for searching contacts by phone"""
    
    def setUp(self):
        super().setUp()
        self.Partner = self.env['res.partner']
        
        # Create test contacts
        self.partner_ahmed = self.Partner.create({
            'name': 'Ahmed Mohamed',
            'phone': '0551234567'
        })
        self.partner_sara = self.Partner.create({
            'name': 'Sara Ali',
            'mobile': '0551111111'
        })
        self.partner_khaled = self.Partner.create({
            'name': 'Khaled Hassan',
            'phone': '+966 55 999 8888'
        })
        self.partner_fatima = self.Partner.create({
            'name': 'Fatima Abdullah',
            'mobile': '055-777-6666'
        })
    
    def test_exact_match_phone(self):
        """Test exact match in phone field"""
        result_ids = self.Partner._name_search(name='0551234567')
        self.assertIn(self.partner_ahmed.id, result_ids)
    
    def test_exact_match_mobile(self):
        """Test exact match in mobile field"""
        result_ids = self.Partner._name_search(name='0551111111')
        self.assertIn(self.partner_sara.id, result_ids)
    
    def test_exact_match_with_formatting(self):
        """Test exact match with different formatting"""
        result_ids = self.Partner._name_search(name='055-123-4567')
        self.assertIn(self.partner_ahmed.id, result_ids)
    
    def test_starts_with_search(self):
        """Test partial search (starts with)"""
        result_ids = self.Partner._name_search(name='055123')
        self.assertIn(self.partner_ahmed.id, result_ids)
    
    def test_starts_with_multiple_results(self):
        """Test partial search returns multiple results"""
        result_ids = self.Partner._name_search(name='055')
        self.assertGreaterEqual(len(result_ids), 3)
    
    def test_international_format_search(self):
        """Test search with international format"""
        result_ids = self.Partner._name_search(name='+966559998888')
        self.assertIn(self.partner_khaled.id, result_ids)
    
    def test_international_format_partial_search(self):
        """Test partial search with international format"""
        result_ids = self.Partner._name_search(name='966559')
        self.assertIn(self.partner_khaled.id, result_ids)
    
    def test_name_search_fallback(self):
        """Test fallback to name search if not a phone number"""
        result_ids = self.Partner._name_search(name='Ahmed')
        self.assertIn(self.partner_ahmed.id, result_ids)
    
    def test_search_respects_limit(self):
        """Test that search respects the limit parameter"""
        result_ids = self.Partner._name_search(name='055', limit=2)
        self.assertLessEqual(len(result_ids), 2)
    
    def test_exact_match_priority_over_partial(self):
        """Test exact match has priority over partial"""
        # Create another partner with number starting with 055123
        self.Partner.create({
            'name': 'Other Partner',
            'phone': '05512399999'
        })
        result_ids = self.Partner._name_search(name='0551234567', limit=1)
        # Should return exact match first
        self.assertEqual(result_ids[0], self.partner_ahmed.id)
    
    def test_no_duplicates_in_results(self):
        """Test no duplicate results"""
        result_ids = self.Partner._name_search(name='055')
        # Check no duplicates
        self.assertEqual(len(result_ids), len(set(result_ids)))
    
    def test_minimum_digits_requirement(self):
        """Test minimum digits requirement for phone search"""
        # Set minimum = 3
        self.env['ir.config_parameter'].sudo().set_param(
            'contact_search_by_phone.min_digits_for_search', '3'
        )
        
        # Search with 2 digits only - should go to name search
        result_ids = self.Partner._name_search(name='05')
        
        # Search with 3 digits - should search in phone
        result_ids = self.Partner._name_search(name='055')
        self.assertGreater(len(result_ids), 0)
    
    def test_search_with_spaces_and_dashes(self):
        """Test search with spaces and dashes"""
        result_ids = self.Partner._name_search(name='055 123 4567')
        self.assertIn(self.partner_ahmed.id, result_ids)
    
    def test_empty_search_returns_all(self):
        """Test empty search returns all results"""
        result_ids = self.Partner._name_search(name='')
        self.assertGreater(len(result_ids), 0)
    
    def test_is_phone_number_detection(self):
        """Test phone number detection"""
        self.assertTrue(self.Partner._is_phone_number('0551234567'))
        self.assertTrue(self.Partner._is_phone_number('055-123-4567'))
        self.assertTrue(self.Partner._is_phone_number('+966551234567'))
        self.assertFalse(self.Partner._is_phone_number('Ahmed'))
        self.assertFalse(self.Partner._is_phone_number('AB'))
    
    def test_suffix_search_skipped_when_exact_match_found(self):
        """
        Test: Skip suffix search when exact match found
        Prevents duplicate results (local + international)
        """
        # Create contact with international format
        partner_intl = self.Partner.create({
            'name': 'International Contact',
            'phone': '+966551234567'
        })
        
        # Create contact with different local number
        partner_local = self.Partner.create({
            'name': 'Local Contact',
            'phone': '0559998888'
        })
        
        # Search with exact local number
        result_ids = self.Partner._name_search(name='0559998888')
        
        # Should find only exact result
        self.assertEqual(len(result_ids), 1)
        self.assertEqual(result_ids[0], partner_local.id)
    
    def test_suffix_search_works_when_no_exact_match(self):
        """
        Test: Suffix search works when no exact match
        Useful for finding local number stored with international format
        """
        # Create contact with long international format
        partner_intl = self.Partner.create({
            'name': 'International Contact',
            'phone': '+19412844875'
        })
        
        # Search with last digits only
        result_ids = self.Partner._name_search(name='9412844875')
        
        # Should find via suffix search
        self.assertIn(partner_intl.id, result_ids)
