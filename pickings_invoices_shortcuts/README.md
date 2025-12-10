# Pickings Invoices Shortcuts

## Overview

This module adds **only the truly missing smart button navigation** between Stock Pickings and Invoices in Odoo 18. After careful audit, we discovered that most functionality already exists - this module adds just 3 missing smart buttons.

## What Already Exists (Preserved)

The following smart buttons already exist in Odoo core modules:

✅ **Sale Order → Invoices** (smart button) - `sale` module  
✅ **Sale Order → Deliveries** (smart button) - `sale_stock` module  
✅ **Stock Picking → Sale Order** (regular field `sale_id`) - `sale_stock` module  
✅ **Invoice → Sale Order** (smart button) - `sale` module ← **Already exists!**

## What This Module Adds

This module adds **only 3 missing smart buttons**:

### 🆕 Stock Picking Form
- **Sale Order** smart button: Upgrades existing `sale_id` field to proper smart button UX
- **Invoices** smart button: Shows count and links to related invoices via sale order

### 🆕 Invoice Form  
- **Deliveries** smart button: Shows count and links to related pickings via sale orders

## Implementation Details

### Dependencies
- **`sale_stock`**: Core dependency that provides all foundation relationships
  - This automatically includes: `base`, `sale`, `stock`, `account`

### Model Extensions

#### Stock Picking (`models/stock_picking.py`)
- **New**: `invoice_count`, `invoice_ids` fields
- **New**: `action_view_invoice()` method  
- **Enhanced**: `action_view_sale_order()` method (smart button version of existing `sale_id` field)

#### Account Move (`models/account_move.py`)
- **New**: `picking_count`, `picking_ids` fields
- **New**: `action_view_picking()` method

### Relationship Strategy

The module leverages existing relationships from `sale_stock`:
- **Picking → Sale Order**: Uses existing `sale_id` field
- **Picking → Invoices**: Via `sale_id.invoice_ids` 
- **Invoice → Pickings**: Via sale orders' `picking_ids` (through existing `line_ids.sale_line_ids.order_id`)

## Installation

```bash
# Dependencies are automatically handled
# sale_stock is usually already installed
```

1. Place module in addons directory
2. Update app list  
3. Install "Pickings Invoices Shortcuts" module

## Smart Button Behavior

### Visibility Logic
- Buttons only show when there are related records (count > 0)
- Invoice buttons only appear on customer invoices/refunds
- Graceful handling when relationships don't exist

### Navigation Logic
- **Single record**: Opens form view directly
- **Multiple records**: Opens list view with domain filter
- **No records**: Action closes (button hidden anyway)

## Example Workflow

1. **Sale Order** → Confirm → **Delivery** created → **Invoice** created
2. **From Delivery**: Smart buttons to view **Sale Order** ↔ **Invoices**  
3. **From Invoice**: Smart buttons to view **Sale Orders** (existing) ↔ **Deliveries** (new)
4. **Round-trip navigation** works in all directions

## Architecture Benefits

### Non-Invasive Design
- Extends existing functionality without replacing it
- Works alongside `sale_stock` module features
- No data migration required

### Performance Optimized  
- Leverages existing computed fields and relationships
- Minimal additional database queries
- Proper `@api.depends` declarations

### UI Consistency
- Follows Odoo core smart button patterns
- Same icons and styling as existing buttons
- Consistent behavior and visibility logic

## Compatibility

- **Odoo Version**: 18.0+
- **Required Modules**: `sale_stock` (includes base dependencies)
- **Optional Modules**: Works with any other sale/stock extensions

## Code Structure

```
pickings_invoices_shortcuts/
├── __manifest__.py                 # Dependencies: sale_stock only
├── README.md
├── models/
│   ├── __init__.py
│   ├── stock_picking.py           # 2 smart buttons: sale order + invoices
│   └── account_move.py            # 1 smart button: pickings only
├── views/
│   ├── stock_picking_views.xml    # Smart button UI for pickings
│   └── account_move_views.xml     # Smart button UI for invoices
└── security/
    └── ir.model.access.csv
```

## What's NOT Included

This module **deliberately excludes**:
- Sale Order extensions (already provided by `sale_stock`)
- Invoice → Sale Order smart button (already exists in `sale` module)
- Duplicate relationship computation (reuses existing fields)
- Complex origin parsing (leverages proper relationship fields)

## Final Scope

**Only 3 smart buttons added:**
1. Stock Picking → Sale Order (smart button upgrade)
2. Stock Picking → Invoices (new functionality)  
3. Invoice → Pickings (new functionality)

**Everything else already exists in Odoo core!** 