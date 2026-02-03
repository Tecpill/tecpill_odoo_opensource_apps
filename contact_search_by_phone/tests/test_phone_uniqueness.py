# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestPhoneUniqueness(TransactionCase):
    """Tests for phone number uniqueness"""
    
    def setUp(self):
        super().setUp()
        self.Partner = self.env['res.partner']
    
    def test_unique_phone_creation(self):
        """Test creating contacts with different phone numbers"""
        partner1 = self.Partner.create({
            'name': 'Partner 1',
            'phone': '0551111111'
        })
        partner2 = self.Partner.create({
            'name': 'Partner 2',
            'phone': '0552222222'
        })
        self.assertTrue(partner1)
        self.assertTrue(partner2)
    
    def test_duplicate_phone_same_format(self):
        """Test preventing duplicate phone with same format"""
        self.Partner.create({
            'name': 'Partner 1',
            'phone': '0551234567'
        })
        with self.assertRaises(ValidationError):
            self.Partner.create({
                'name': 'Partner 2',
                'phone': '0551234567'
            })
    
    def test_duplicate_phone_different_format(self):
        """Test preventing duplicate phone with different format (spaces/symbols)"""
        self.Partner.create({
            'name': 'Partner 1',
            'phone': '0551234567'
        })
        with self.assertRaises(ValidationError):
            self.Partner.create({
                'name': 'Partner 2',
                'phone': '055-123-4567'
            })
    
    def test_duplicate_mobile_prevention(self):
        """Test preventing duplicate mobile number"""
        self.Partner.create({
            'name': 'Partner 1',
            'mobile': '0551234567'
        })
        with self.assertRaises(ValidationError):
            self.Partner.create({
                'name': 'Partner 2',
                'mobile': '055 123 4567'
            })
    
    def test_null_phones_allowed(self):
        """Test allowing multiple NULL values"""
        partner1 = self.Partner.create({'name': 'Partner 1'})
        partner2 = self.Partner.create({'name': 'Partner 2'})
        self.assertFalse(partner1.phone)
        self.assertFalse(partner2.phone)
    
    def test_empty_phones_allowed(self):
        """Test allowing multiple empty values"""
        partner1 = self.Partner.create({'name': 'Partner 1', 'phone': ''})
        partner2 = self.Partner.create({'name': 'Partner 2', 'phone': ''})
        self.assertEqual(partner1.phone, '')
        self.assertEqual(partner2.phone, '')
    
    def test_update_to_duplicate_phone(self):
        """Test preventing update to duplicate phone"""
        partner1 = self.Partner.create({
            'name': 'Partner 1',
            'phone': '0551111111'
        })
        partner2 = self.Partner.create({
            'name': 'Partner 2',
            'phone': '0552222222'
        })
        with self.assertRaises(ValidationError):
            partner2.write({'phone': '0551111111'})
    
    def test_phone_and_mobile_can_be_same_on_different_partners(self):
        """Test: Can Contact A phone equal Contact B mobile?"""
        partner1 = self.Partner.create({
            'name': 'Partner 1',
            'phone': '0551234567'
        })
        # Should fail because mobile_clean will match phone_clean
        with self.assertRaises(ValidationError):
            self.Partner.create({
                'name': 'Partner 2',
                'mobile': '0551234567'
            })
    
    def test_disable_uniqueness_check(self):
        """Test disabling uniqueness check via context"""
        self.Partner.create({
            'name': 'Partner 1',
            'phone': '0551234567'
        })
        # Create with same number but disable check
        partner2 = self.Partner.with_context(enforce_unique_phones=False).create({
            'name': 'Partner 2',
            'phone': '055-123-4567'
        })
        self.assertTrue(partner2)
    
    def test_cross_field_uniqueness_mobile_vs_phone(self):
        """
        Test cross-field uniqueness prevention:
        Contact B mobile cannot equal Contact A phone
        """
        # Create first contact with phone
        partner1 = self.Partner.create({
            'name': 'Partner 1',
            'phone': '0551234567'
        })
        self.assertEqual(partner1.phone_clean, '551234567')
        
        # Try to create second contact with mobile as same number
        with self.assertRaises(ValidationError) as context:
            self.Partner.create({
                'name': 'Partner 2',
                'mobile': '055-123-4567'
            })
        
        # Verify error message
        self.assertIn('already used', str(context.exception))
    
    def test_cross_field_uniqueness_phone_vs_mobile(self):
        """
        Test cross-field uniqueness prevention:
        Contact B phone cannot equal Contact A mobile
        """
        # Create first contact with mobile
        partner1 = self.Partner.create({
            'name': 'Partner 1',
            'mobile': '0559876543'
        })
        self.assertEqual(partner1.mobile_clean, '559876543')
        
        # Try to create second contact with phone as same number
        with self.assertRaises(ValidationError) as context:
            self.Partner.create({
                'name': 'Partner 2',
                'phone': '055 987 6543'
            })
        
        # Verify error message
        self.assertIn('already used', str(context.exception))
