# Troubleshooting Guide - Contact Search by Phone

## Issue: Search not finding customers by phone number

### Symptoms
- Customer exists with phone `(828)-316-0593`
- Searching for `828316` or `8283160593` returns no results
- Only shows "Create '828316'" option

### Root Causes

#### 1. **Signature Mismatch (Most Common in Odoo 18)**

**Problem:** `_name_search` doesn't have `name_get_uid` parameter

**Error in logs:**
```
TypeError: _name_search() got an unexpected keyword argument 'name_get_uid'
```

**Solution:** ✅ Fixed in version 18.0.2.0.0
- Added `name_get_uid` parameter to signature
- Pass `access_rights_uid=name_get_uid` to `_search()` calls

#### 2. **Empty phone_clean Fields**

**Problem:** Computed fields not calculated for existing records

**Check:**
```python
# In Odoo shell
partner = env['res.partner'].search([('phone', 'ilike', '828')], limit=1)
print(f"Phone: {partner.phone}")
print(f"phone_clean: {partner.phone_clean}")  # Should NOT be False
```

**Solution:**
```python
# Recompute for all partners
partners = env['res.partner'].with_context(active_test=False).search([])
partners._compute_phone_normalized()
env.cr.commit()
```

#### 3. **Minimum Digits Threshold**

**Problem:** Search term too short

**Check:**
```python
min_digits = env['ir.config_parameter'].get_param(
    'contact_search_by_phone.min_digits_for_search'
)
print(f"Minimum digits: {min_digits}")  # Default: 3
```

**Solution:** Adjust in Settings → Contact Phone Search

### Diagnostic Steps

#### Step 1: Run Diagnostic Script

```bash
cd /home/sasmnka/odoo18
./odoo-bin shell -c odoo18.conf -d 18odoo18
```

```python
exec(open('/tmp/diagnose_phone_search.py').read())
```

Expected output:
```
1. Found X partners with '828' in phone:
  • ID: 123, Name: John Doe
    Phone: (828)-316-0593
    phone_clean: 8283160593  ← Should be filled
    phone_clean_rev: 3950613828  ← Should be filled
```

#### Step 2: Check Logs for TypeError

```bash
tail -f /var/log/odoo/odoo-server.log | grep -i "name_search\|TypeError"
```

Look for:
- `TypeError: unexpected keyword argument 'name_get_uid'`
- `UndefinedColumn: column res_partner.phone_clean_rev does not exist`

#### Step 3: Test Search Manually

```python
# Test normalization
env['res.partner']._normalize_phone('(828)-316-0593')
# Expected: '8283160593'

# Test detection
env['res.partner']._is_phone_number('828316')
# Expected: True

# Test search
result_ids = env['res.partner']._name_search('828316')
# Expected: [list of IDs]
```

#### Step 4: Test in UI

1. Go to Sales → Quotations → Create
2. Click on Customer field
3. Type: `828316`
4. Should show customer with phone `(828)-316-0593`

### Quick Fixes

#### Fix 1: Update Module

```bash
cd /home/sasmnka/odoo18
./odoo-bin -c odoo18.conf -d 18odoo18 -u contact_search_by_phone --stop-after-init
```

#### Fix 2: Recompute Fields

```bash
./odoo-bin shell -c odoo18.conf -d 18odoo18
```

```python
exec(open('/tmp/fix_phone_clean.py').read())
```

#### Fix 3: Check Database Columns

```sql
-- Check if columns exist
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'res_partner' 
AND column_name LIKE 'phone_%';

-- Expected:
-- phone_clean
-- phone_clean_rev
```

### Advanced Debugging

#### Enable Debug Logging

Add to config file:
```ini
log_handler = odoo.addons.contact_search_by_phone:DEBUG
```

#### Test Query Performance

```python
# Test exact match
import time
start = time.time()
result = env['res.partner'].search([('phone_clean', '=', '8283160593')])
print(f"Exact match: {time.time() - start:.4f}s")

# Test prefix match
start = time.time()
result = env['res.partner'].search([('phone_clean', '=like', '828316%')])
print(f"Prefix match: {time.time() - start:.4f}s")
```

#### Check Indexes

```sql
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'res_partner' 
AND indexname LIKE '%phone%';

-- Expected:
-- res_partner_phone_clean_pattern_idx
-- res_partner_phone_clean_rev_pattern_idx
```

### Still Not Working?

1. **Check module installed:**
   ```python
   env['ir.module.module'].search([('name', '=', 'contact_search_by_phone')]).state
   # Should be: 'installed'
   ```

2. **Check field values:**
   ```python
   partner = env['res.partner'].browse(123)  # Replace with actual ID
   partner.read(['phone', 'phone_clean', 'phone_clean_rev'])
   ```

3. **Force recompute:**
   ```python
   partner.write({'phone': partner.phone})  # Trigger compute
   ```

4. **Clear cache:**
   ```python
   env.registry.clear_cache()
   ```

### Prevention

1. **Always upgrade module after changes:**
   ```bash
   ./odoo-bin -c odoo.conf -d dbname -u contact_search_by_phone --stop-after-init
   ```

2. **Monitor logs during search:**
   ```bash
   tail -f /var/log/odoo/odoo-server.log | grep contact_search
   ```

3. **Test after install:**
   ```python
   # Run tests
   env['res.partner']._name_search('test123')
   ```

## Support

If issue persists, provide:
1. Odoo version
2. Module version
3. Error logs
4. Output of diagnostic script
5. Database column list
6. Test search results
