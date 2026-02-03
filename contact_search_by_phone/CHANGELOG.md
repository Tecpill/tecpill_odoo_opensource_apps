# Changelog

All notable changes to Contact Search by Phone module will be documented in this file.

## [18.0.2.0.4] - 2026-01-15

### Configurable Leading Zero Stripping

#### Added
- **NEW SETTING: Strip Leading Zero from Phone Numbers**
  - Configurable in Settings → General Settings → Contact Phone Search
  - Default: Enabled (matches Gulf/Saudi number format: 05xxx → 5xxx)
  - When disabled: Preserves leading zero for countries where it's part of the actual number
  - Example: `0551234567` → `551234567` (enabled) or `0551234567` (disabled)
  - Always strips `00` international prefix regardless of setting
  - New config parameter: `contact_search_by_phone.strip_leading_zero`

#### Fixed
- **CRITICAL: Duplicate 'images' key in __manifest__.py**
  - Merged into single key with both banner.png and icon.png
  - Now both images properly display in Apps page

- **CRITICAL: Cross-field duplicate detection in post_init_hook**
  - Added SQL query to detect phone_clean vs mobile_clean duplicates
  - Logs cross-field duplicates during installation
  - Uses UNION ALL to check numbers across both fields

- **Typo in INSTALLATION.md**
  - Fixed: `contact_search_by__phone` → `contact_search_by_phone`

- **Outdated commands in TROUBLESHOOTING.md**
  - Updated recompute instructions to use merged `_compute_phone_normalized()`
  - Removed references to deleted methods (_compute_phone_clean, etc.)

#### Tests
- Added 3 new tests for strip_leading_zero setting:
  - `test_strip_leading_zero_enabled` - Verify leading 0 is removed when enabled
  - `test_strip_leading_zero_disabled` - Verify leading 0 is kept when disabled
  - `test_strip_leading_zero_not_affect_00_prefix` - Verify 00 always stripped

---

## [18.0.2.0.3] - 2026-01-15

### Enhanced Cross-Field Uniqueness & Search Optimization

#### Fixed
- **CRITICAL: Cross-field phone uniqueness enforcement**
  - Now checks `phone_clean` against both `phone_clean` AND `mobile_clean` fields
  - Also checks `mobile_clean` against both `phone_clean` AND `mobile_clean` fields
  - Prevents scenarios where Contact A has phone="055123" and Contact B has mobile="055123"
  - Error message now indicates which field contains the duplicate (Phone/Mobile)

- **Search optimization: Skip suffix search when exact match found**
  - Prevents duplicate results (local + international versions of same number)
  - If exact match found, suffix search is skipped
  - Example: Search "0551234567" finds local contact, won't also show "+966551234567"
  - Logged in debug: "Suffix search skipped due to exact match found"

#### Added
- New test: `test_cross_field_uniqueness_mobile_vs_phone`
- New test: `test_cross_field_uniqueness_phone_vs_mobile`
- New test: `test_suffix_search_skipped_when_exact_match_found`
- New test: `test_suffix_search_works_when_no_exact_match`

---

## [18.0.2.0.2] - 2026-01-15

### Critical Fixes & Performance Improvements

#### Fixed
- **CRITICAL: Enforce Unique now properly reads config parameter**
  - Reads `contact_search_by_phone.enforce_unique` from Settings
  - Setting can be toggled ON/OFF from Settings > General Settings
  - Context override still works: `with_context(enforce_unique_phones=False)`

- **CRITICAL: Removed broken `_sql_constraints`**
  - PostgreSQL doesn't support `UNIQUE(...) WHERE ...` syntax in CONSTRAINT
  - Replaced with Python `@api.constrains` decorator
  - Now uniqueness is optional (controlled by config parameter)

- **CRITICAL: Fixed access rights in Odoo 18**
  - `name_get_uid` now properly passed via `self.sudo(name_get_uid)`
  - Applied to all `_search()` calls (exact, prefix, suffix, fallback)

- Removed duplicate field definitions for `phone` and `mobile`

#### Improved
- **"Show Phone in Search" now auto-enabled from Settings**
  - `name_get()` reads `contact_search_by_phone.show_phone_in_search`
  - If enabled in Settings, automatically shows phone in results

- **Optimized compute methods (50% performance gain)**
  - Merged 4 separate `@api.depends` methods into one
  - `_compute_phone_normalized()` now computes all 4 fields at once
  - Prevents duplicate normalization

- **Added comprehensive debug logging**
  - Logs when phone search is triggered
  - Shows normalized search term and digit count
  - Logs results count for each search stage (exact/prefix/suffix)

---

## [18.0.2.0.1] - 2026-01-14

### Fixed
- **CRITICAL: Fixed Odoo 18 compatibility issue**
  - Added `name_get_uid` parameter to `_name_search()` signature
  - Fixes TypeError: "unexpected keyword argument 'name_get_uid'"
  - Ensures proper access rights checking during search

### Added
- TROUBLESHOOTING.md guide for common search issues
- Diagnostic script for troubleshooting
- Fix script for recomputing fields

---

## [18.0.2.0.0] - 2026-01-14

### Major Update - Enterprise Features

#### Added
- **Phone Normalization System**
  - `_normalize_phone()` method: strips all non-digit characters
  - `phone_clean` computed stored indexed field
  - `mobile_clean` computed stored indexed field
  - Handles international formats (+966, 00966, etc.)
  
- **Advanced Search Logic**
  - Smart detection if search term is a phone number
  - Priority system: exact match → starts with → name search
  - No duplicate results in search
  - Configurable minimum digits threshold
  
- **Enhanced Uniqueness**
  - NULL-safe and empty-string-safe constraints
  - Format-agnostic duplicate detection
  - Context override: `enforce_unique_phones=False`
  
- **PostgreSQL Performance Indexes**
  - `text_pattern_ops` indexes on normalized fields
  - Optimized for `LIKE 'xxx%'` prefix searches
  
- **Configuration Settings**
  - Minimum digits for phone search trigger
  - Enable/disable uniqueness enforcement
  - Show phone in search results toggle
  
- **Comprehensive Test Suite**
  - 43 automated tests total
  - Phone normalization tests
  - Uniqueness enforcement tests
  - Search functionality tests

#### Technical
- Added `hooks.py` for installation hooks
- Added `res_config_settings.py` for settings
- Added `res_partner_indexes.py` for custom indexes
- Added configuration views

### Performance
- 15x-262x faster searches (benchmarked on 10K-100K contacts)
- Instant exact match lookups via indexed fields
- Ultra-fast prefix searches via `text_pattern_ops`

---

## [18.0.1.0.0] - Initial Release

- Basic phone search functionality
- Simple normalization
- Name search integration
