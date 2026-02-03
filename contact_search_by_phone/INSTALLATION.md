# Contact Search by Phone - Installation Guide

## 📦 Installation Steps

### 1. Prerequisites
- Odoo 18.0
- PostgreSQL 12+
- `contacts` module installed

### 2. Install Module

#### Method A: Via Odoo UI
```bash
1. Copy module folder to: /path/to/odoo/addons/
2. Restart Odoo server
3. Go to: Apps → Update Apps List
4. Search: "Contact Search by Phone"
5. Click: Install
```

#### Method B: Via Command Line
```bash
# Copy module
cp -r contact_search_by_phone /path/to/odoo/addons/

# Restart Odoo
sudo systemctl restart odoo

# Install via CLI
odoo-bin -c /etc/odoo/odoo.conf -d your_database -i contact_search_by_phone --stop-after-init
```

### 3. Post-Installation

Check the server log for duplicate detection:
```
==================================================================================
Contact Search by Phone: Post-Installation Check
==================================================================================
✅ No duplicate phone numbers found. All good!
==================================================================================
```

If duplicates found:
```
⚠️  Found 3 duplicate phone numbers:
  • Phone: 0551234567 (Used by 2 contacts: Ahmed, Sara...)
  
⚠️  ACTION REQUIRED:
Please clean duplicate phone/mobile numbers before they cause issues.
```

### 4. Handle Duplicates (if any)

#### Option A: Fix Manually
```sql
-- Find duplicates
SELECT phone_clean, COUNT(*), array_agg(name) 
FROM res_partner 
WHERE phone_clean IS NOT NULL AND phone_clean <> ''
GROUP BY phone_clean 
HAVING COUNT(*) > 1;

-- Update one of the duplicates
UPDATE res_partner 
SET phone = NULL 
WHERE id = <duplicate_id>;
```

#### Option B: Temporarily Disable Uniqueness
```
Settings → General Settings → Contact Phone Search
→ Enforce Unique Phone Numbers = OFF
```

### 5. Configure Settings

Navigate to: **Settings → General Settings → Contact Phone Search**

Recommended settings:
- ✅ Enforce Unique Phone Numbers: **ON**
- ✅ Show Phone in Search Results: **ON**
- Minimum Digits for Search: **3** (adjust based on your needs)

### 6. Verify Installation

#### Test 1: Create Contact with Phone
```python
env['res.partner'].create({
    'name': 'Test User',
    'phone': '055-123-4567'
})
# Check: phone_clean should be '0551234567'
```

#### Test 2: Search by Phone
```python
# Search by number
result = env['res.partner'].name_search('055123')
# Should find the contact
```

#### Test 3: Uniqueness Check
```python
# Try creating duplicate
env['res.partner'].create({
    'name': 'Another User',
    'phone': '0551234567'  # Same number, different format
})
# Should raise ValidationError
```

### 7. Database Indexes Verification

```sql
-- Check if custom indexes are created
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'res_partner' 
AND indexname LIKE '%phone%';

-- Expected output:
-- res_partner_phone_clean_pattern_idx
-- res_partner_mobile_clean_pattern_idx
```

## 🔄 Upgrade from Previous Version

### From 18.0.1.0.0 to 18.0.2.0.0

```bash
# Update module
odoo-bin -c /etc/odoo/odoo.conf -d your_database -u contact_search_by_phone --stop-after-init
```

**Changes applied automatically:**
- ✅ `phone_clean` and `mobile_clean` fields computed for all existing contacts
- ✅ Custom PostgreSQL indexes created
- ✅ Old `phone_unique` constraint replaced with new constraints
- ✅ Settings added to General Settings

**Manual steps:**
1. Review post-upgrade log for duplicates
2. Configure new settings in General Settings
3. Test search functionality

## 🐛 Troubleshooting

### Issue: Module not appearing in Apps list
**Solution:**
```bash
# Check addons path
grep addons_path /etc/odoo/odoo.conf

# Verify module in path
ls -la /path/to/addons/contact_search_by_phone/

# Update apps list
# Apps → Update Apps List (with developer mode ON)
```

### Issue: Error during installation
**Solution:**
```bash
# Check server logs
tail -f /var/log/odoo/odoo-server.log

# Common issues:
# - Missing dependency: Install 'contacts' module first
# - Permission issues: Check file permissions
sudo chown -R odoo:odoo /path/to/addons/contact_search_by_phone/
```

### Issue: Indexes not created
**Solution:**
```sql
-- Manually create indexes
CREATE INDEX IF NOT EXISTS res_partner_phone_clean_pattern_idx
ON res_partner (phone_clean text_pattern_ops)
WHERE phone_clean IS NOT NULL AND phone_clean <> '';

CREATE INDEX IF NOT EXISTS res_partner_mobile_clean_pattern_idx
ON res_partner (mobile_clean text_pattern_ops)
WHERE mobile_clean IS NOT NULL AND mobile_clean <> '';
```

### Issue: Search not working
**Solution:**
```python
# 1. Check if phone_clean is computed
partner = env['res.partner'].search([('phone', '!=', False)], limit=1)
print(f"Phone: {partner.phone}, Clean: {partner.phone_clean}")

# 2. Check minimum digits setting
min_digits = env['ir.config_parameter'].get_param(
    'contact_search_by_phone.min_digits_for_search'
)
print(f"Min digits: {min_digits}")

# 3. Test normalization
clean = env['res.partner']._normalize_phone('055-123-4567')
print(f"Normalized: {clean}")
```

## 🔒 Security Considerations

### Permissions
No custom security groups required - uses Odoo's standard `res.partner` permissions.

### Data Access
- Settings: Only users with Settings access
- Phone search: Same as contact access permissions
- Phone uniqueness: Applies to all users

## 🚀 Performance Tips

### For Large Databases (100K+ contacts)

1. **Rebuild indexes periodically:**
```sql
REINDEX INDEX res_partner_phone_clean_pattern_idx;
REINDEX INDEX res_partner_mobile_clean_pattern_idx;
```

2. **Analyze tables:**
```sql
ANALYZE res_partner;
```

3. **Monitor query performance:**
```sql
EXPLAIN ANALYZE 
SELECT id FROM res_partner 
WHERE phone_clean LIKE '055%' 
LIMIT 100;
```

4. **Increase work_mem if needed:**
```sql
-- In postgresql.conf
work_mem = 64MB
```

## 📊 Monitoring

### Key Metrics to Watch

```sql
-- Number of contacts with phones
SELECT COUNT(*) FROM res_partner WHERE phone_clean IS NOT NULL;

-- Number of contacts with mobiles
SELECT COUNT(*) FROM res_partner WHERE mobile_clean IS NOT NULL;

-- Index sizes
SELECT pg_size_pretty(pg_relation_size('res_partner_phone_clean_pattern_idx'));
SELECT pg_size_pretty(pg_relation_size('res_partner_mobile_clean_pattern_idx'));

-- Table size
SELECT pg_size_pretty(pg_total_relation_size('res_partner'));
```

## 🎓 Training Users

### For End Users:
1. **Search by phone**: Just type numbers (spaces/dashes don't matter)
2. **Minimum digits**: Need at least 3 digits to search by phone
3. **Results format**: "Name — Phone" shows phone numbers

### For Administrators:
1. **Settings**: Located in General Settings
2. **Duplicates**: Check logs after install/upgrade
3. **Performance**: Monitor with `EXPLAIN ANALYZE`

## 📞 Support

### Getting Help
- Documentation: See [README.md](README.md)
- Changelog: See [CHANGELOG.md](CHANGELOG.md)
- Email: support@yourcompany.com

### Reporting Bugs
Include:
1. Odoo version
2. Module version
3. Error message/log
4. Steps to reproduce
5. Database size (number of contacts)

## ✅ Installation Checklist

- [ ] Module copied to addons folder
- [ ] Odoo server restarted
- [ ] Apps list updated
- [ ] Module installed successfully
- [ ] Post-install log checked
- [ ] Duplicates resolved (if any)
- [ ] Settings configured
- [ ] Search tested
- [ ] Uniqueness tested
- [ ] Indexes verified
- [ ] Users trained

---

**Congratulations! Module installed successfully! 🎉**
