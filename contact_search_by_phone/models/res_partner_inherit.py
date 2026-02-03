# -*- coding: utf-8 -*-

import re
import logging
from odoo import models, fields, api, _, tools
from odoo.osv import expression
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'
    
    # Cleaned, stored and indexed fields for fast and accurate search
    phone_clean = fields.Char(
        string='Phone (Normalized)',
        compute='_compute_phone_normalized',
        store=True,
        index=True,
        help="Phone number with only digits, automatically computed"
    )
    mobile_clean = fields.Char(
        string='Mobile (Normalized)',
        compute='_compute_phone_normalized',
        store=True,
        index=True,
        help="Mobile number with only digits, automatically computed"
    )
    
    # Reversed fields for fast suffix search (Ends-with)
    phone_clean_rev = fields.Char(
        string='Phone (Normalized, Reversed)',
        compute='_compute_phone_normalized',
        store=True,
        index=True,
        help="Reversed phone number for fast suffix search"
    )
    mobile_clean_rev = fields.Char(
        string='Mobile (Normalized, Reversed)',
        compute='_compute_phone_normalized',
        store=True,
        index=True,
        help="Reversed mobile number for fast suffix search"
    )

    def _register_hook(self):
        """Register mobile field dependency if available"""
        super()._register_hook()
        # Add mobile to depends if the field exists
        if 'mobile' in self._fields:
            phone_clean_field = self._fields['phone_clean']
            if phone_clean_field.depends and 'mobile' not in phone_clean_field.depends:
                phone_clean_field.depends = phone_clean_field.depends + ('mobile',)

    def _strip_leading_zero_enabled(self) -> bool:
        """
        Helper method to check if strip_leading_zero setting is enabled
        Returns:
            bool: True if setting is enabled (default), False otherwise
        """
        value = self.env['ir.config_parameter'].sudo().get_param(
            'contact_search_by_phone.strip_leading_zero',
            default='True'
        )
        return tools.str2bool(value)

    @api.model
    def _normalize_phone(self, phone_number, strip_leading_zero=None):
        """
        Normalize phone number: Remove everything except digits
        and remove 00 prefix (for international numbers) or single leading 0
        Args:
            phone_number (str): The raw phone number
        Returns:
            str: The cleaned number (digits only) or False
        """
        if not phone_number:
            return False
        # Remove everything except digits
        clean = re.sub(r'\D', '', phone_number or '')
        # Remove 00 prefix (00966 → 966)
        if clean.startswith('00'):
            clean = clean[2:]
        # Remove single leading 0 (0551234567 → 551234567) - if setting enabled
        elif clean.startswith('0') and len(clean) > 1:
            # Check setting
            strip_zero = self.env['ir.config_parameter'].sudo().get_param(
                'contact_search_by_phone.strip_leading_zero', 'True'
            )
            if tools.str2bool(strip_zero):
                clean = clean[1:]
        return clean if clean else False

    @api.depends('phone')
    def _compute_phone_normalized(self):
        """Compute all normalized phone fields at once to avoid duplicate processing"""
        strip = self._strip_leading_zero_enabled()
        for partner in self:
            # Normalize phone
            phone_normalized = self._normalize_phone(partner.phone, strip_leading_zero=strip)
            partner.phone_clean = phone_normalized
            partner.phone_clean_rev = phone_normalized[::-1] if phone_normalized else False
            
            # Normalize mobile (safely handle if field doesn't exist)
            mobile_value = getattr(partner, 'mobile', False)
            mobile_normalized = self._normalize_phone(mobile_value, strip_leading_zero=strip)
            partner.mobile_clean = mobile_normalized
            partner.mobile_clean_rev = mobile_normalized[::-1] if mobile_normalized else False

    @api.constrains('phone')
    def _check_phone_uniqueness(self):
        """
        Python constraint to enforce phone uniqueness based on config parameter
        Checks cross-field: phone_clean vs mobile_clean across all records
        Only checks if enforce_unique setting is enabled
        """
        # Check if uniqueness enforcement is enabled
        enforce_unique = self.env['ir.config_parameter'].sudo().get_param(
            'contact_search_by_phone.enforce_unique', default='True'
        )
        
        # Allow context override (enforce_unique_phones=False to skip check)
        if not tools.str2bool(enforce_unique) or not self.env.context.get('enforce_unique_phones', True):
            return
        
        for partner in self:
            # Check phone_clean against both phone_clean and mobile_clean of other records (cross-field)
            if partner.phone_clean:
                duplicate = self.search([
                    ('id', '!=', partner.id),
                    '|',
                    ('phone_clean', '=', partner.phone_clean),
                    ('mobile_clean', '=', partner.phone_clean)
                ], limit=1)
                if duplicate:
                    field_name = 'Mobile' if duplicate.mobile_clean == partner.phone_clean else 'Phone'
                    raise ValidationError(
                        _('Phone number %s is already used by %s (%s field)') % 
                        (partner.phone, duplicate.display_name, field_name)
                    )
            
            # Check mobile_clean against both phone_clean and mobile_clean of other records (cross-field)
            if partner.mobile_clean:
                duplicate = self.search([
                    ('id', '!=', partner.id),
                    '|',
                    ('phone_clean', '=', partner.mobile_clean),
                    ('mobile_clean', '=', partner.mobile_clean)
                ], limit=1)
                if duplicate:
                    field_name = 'Mobile' if duplicate.mobile_clean == partner.mobile_clean else 'Phone'
                    mobile_value = getattr(partner, 'mobile', '')
                    raise ValidationError(
                        _('Mobile number %s is already used by %s (%s field)') % 
                        (mobile_value, duplicate.display_name, field_name)
                    )

    def name_get(self):
        """
        Override to display phone number alongside contact name in search results.

        - يحترم الإعداد show_phone_in_search
        - يحافظ على أداء جيد في Odoo 19
        - آمن حتى لو super().name_get() غير متوفر (fallback)
        """
        # اقرأ الإعداد مرة واحدة فقط
        show_phone = tools.str2bool(
            self.env['ir.config_parameter'].sudo().get_param(
                'contact_search_by_phone.show_phone_in_search',
                default='True'
            )
        ) or self.env.context.get('show_phone_in_name', False)

        # إذا عرض الهاتف ملغي → استخدم الـ name_get الافتراضي قدر الإمكان
        if not show_phone:
            try:
                return super().name_get()
            except AttributeError:
                # Fallback آمن لو ما في name_get في super
                return [(partner.id, partner.name or '') for partner in self]

        # حاول تجيب الأسماء الافتراضية مرة واحدة فقط
        try:
            default_results = super().name_get()
        except AttributeError:
            # Fallback: استخدم name العادي بدون سوبر
            default_results = [(partner.id, partner.name or '') for partner in self]

        # حوّلها لقاموس: {id: name}
        default_names = dict(default_results)

        result = []
        for partner in self:
            # الاسم الافتراضي
            name = default_names.get(partner.id, partner.name or '')

            # الهاتف (phone أو mobile من phone_validation)
            mobile = getattr(partner, 'mobile', False)
            phone = partner.phone or mobile

            # أضف رقم الهاتف لو موجود
            if phone:
                name = f"{name} — {phone}"

            result.append((partner.id, name))

        return result

    @api.model
    def _is_phone_number(self, search_term):
        """
        Determine if the input text looks like a phone number
        Args:
            search_term (str): The text to check
        Returns:
            bool: True if it looks like a phone number
        """
        if not search_term:
            return False
        
        # Get minimum digits from settings
        min_digits = self.env['ir.config_parameter'].sudo().get_param(
            'contact_search_by_phone.min_digits_for_search', default='3'
        )
        min_digits = int(min_digits)
        
        # Count digits in the text
        digits_only = re.sub(r'\D', '', search_term)
        return len(digits_only) >= min_digits

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100, order=None):
        """
        Main search method used from the user interface
        Calls _name_search for the actual logic
        """
        # Call _name_search with proper parameters
        ids = self._name_search(name=name, args=args, operator=operator, limit=limit, order=order)
        return self.browse(ids).name_get()

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None, order=None):
        """
        Smart advanced search with priority system (Odoo 19 Compatible):
        1. If input looks like a phone number:
           - Exact match in normalized numbers
           - Starts with (prefix search) in normalized numbers
           - Ends with (suffix search for international numbers)
        2. Default name search
        
        Prevents duplicates and respects limit precisely
        
        Args:
            name: The text to search for
            args: Additional domain
            operator: Operator (ilike by default)
            limit: Maximum number of results
            name_get_uid: User ID for permission check (Odoo 19)
            order: Results ordering
        """
        if args is None:
            args = []
        
        domain = args.copy()
        found_ids = []
        
        if name and self._is_phone_number(name):
            # Normalize search number (respect strip_leading_zero setting)
            strip = self._strip_leading_zero_enabled()
            search_clean = self._normalize_phone(name, strip_leading_zero=strip)
            
            if search_clean:
                digits_count = len(search_clean)
                _logger.debug(
                    f"Phone search triggered: '{name}' → '{search_clean}' ({digits_count} digits)"
                )
                
                # 1. Search for exact match
                exact_domain = [
                    '|',
                    ('phone_clean', '=', search_clean),
                    ('mobile_clean', '=', search_clean)
                ]
                # Use sudo with name_get_uid if provided for access rights
                search_model = self.sudo(name_get_uid) if name_get_uid else self
                exact_ids = search_model._search(
                    expression.AND([exact_domain, domain]),
                    limit=limit,
                    order=order
                )
                
                if exact_ids:
                    found_ids.extend(exact_ids)
                    _logger.debug(f"Exact match found: {len(exact_ids)} result(s)")
                    # Skip suffix search if exact match found to avoid duplicates
                    # (e.g., don't show +966551234567 when 0551234567 exact match exists)
                    skip_suffix = True
                else:
                    skip_suffix = False
                
                # 2. Partial search (Starts With) - Prefix Search
                if len(found_ids) < limit:
                    remaining_limit = limit - len(found_ids)
                    prefix_domain = [
                        '|',
                        ('phone_clean', '=like', search_clean + '%'),
                        ('mobile_clean', '=like', search_clean + '%'),
                    ]
                    if found_ids:
                        prefix_domain = expression.AND([prefix_domain, [('id', 'not in', found_ids)]])
                    
                    prefix_ids = search_model._search(
                        expression.AND([prefix_domain, domain]),
                        limit=remaining_limit,
                        order=order
                    )
                    
                    if prefix_ids:
                        found_ids.extend(prefix_ids)
                        _logger.debug(f"Prefix match found: {len(prefix_ids)} result(s)")
                
                # 3. Suffix Search (for long numbers) - only if no exact match
                # Very useful when number is stored with different country code
                # Example: stored 19412844875, search 9412844875
                # Skip if exact match found to prevent showing both local and international versions
                if not skip_suffix and len(found_ids) < limit and len(search_clean) >= 7:
                    remaining_limit = limit - len(found_ids)
                    # Reverse number for fast search
                    search_rev = search_clean[::-1]
                    suffix_domain = [
                        '|',
                        ('phone_clean_rev', '=like', search_rev + '%'),
                        ('mobile_clean_rev', '=like', search_rev + '%'),
                    ]
                    if found_ids:
                        suffix_domain = expression.AND([suffix_domain, [('id', 'not in', found_ids)]])
                    
                    suffix_ids = search_model._search(
                        expression.AND([suffix_domain, domain]),
                        limit=remaining_limit,
                        order=order
                    )
                    
                    if suffix_ids:
                        found_ids.extend(suffix_ids)
                        _logger.debug(f"Suffix match found: {len(suffix_ids)} result(s)")
                elif skip_suffix:
                    _logger.debug("Suffix search skipped due to exact match found")
                
                # If we found results, return them
                if found_ids:
                    _logger.debug(f"Total phone search results: {len(found_ids)}")
                    return found_ids
                else:
                    _logger.debug("No phone matches found, falling back to name search")
        
        # 3. Default name search - use standard logic
        try:
            return super()._name_search(
                name=name, 
                args=args, 
                operator=operator, 
                limit=limit, 
                name_get_uid=name_get_uid,
                order=order
            )
        except (AttributeError, TypeError):
            # If _name_search not found in base class or doesn't support name_get_uid, use _search
            name_domain = [(self._rec_name, operator, name)] if name else []
            search_model = self.sudo(name_get_uid) if name_get_uid else self
            return search_model._search(
                expression.AND([name_domain, args or []]),
                limit=limit,
                order=order
            )

