# Contact Search by Phone

Search for contacts using phone or mobile numbers in Odoo 16.

## Features

✅ **Smart Phone Search**
- Search contacts by typing full or partial phone numbers
- Works with any phone format: (828)-316-0593, 828-316-0593, 8283160593
- Automatic normalization (removes spaces, dashes, parentheses)

✅ **Fast Performance**
- PostgreSQL indexes for instant search
- Prefix and suffix search support
- Stored computed fields

✅ **Optional Uniqueness**
- Prevent duplicate phone numbers
- NULL-safe and empty-safe constraints
- Configurable via Settings

## Installation

1. Copy this module to your Odoo addons directory
2. Update Apps list
3. Install "Contact Search by Phone"

## Usage

### Search by Phone
1. Go to any contact selection field (Customer, Vendor, etc.)
2. Type a phone number (full or partial): `828`, `8283160593`, `828-316`
3. Contact will appear in results

### Configuration
Go to: **Settings → General Settings → Contact Search by Phone**

- **Minimum digits for search**: Default 3 (trigger phone search)
- **Enforce unique phones**: Prevent duplicate phone numbers
- **Show phone in search**: Display phone in dropdown results

## Technical Details

### Added Fields
- `phone_clean`: Normalized phone (stored, indexed)
- `mobile_clean`: Normalized mobile (stored, indexed)
- `phone_clean_rev`: Reversed phone for suffix search
- `mobile_clean_rev`: Reversed mobile for suffix search

### Search Priority
1. Exact match on normalized phone/mobile
2. Prefix match (starts with)
3. Suffix match (ends with) - for international numbers
4. Standard name search fallback

### Normalization Rules
- Removes all non-digit characters
- Handles `00` prefix (00966 → 966)
- Example: `(828)-316-0593` → `8283160593`

## Testing

Run automated tests:
```bash
./odoo-bin -c odoo.conf -d dbname -u contact_search_by_phone --test-enable --stop-after-init
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md)

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## License

LGPL-3

## Author

Your Company
