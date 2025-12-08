# Changelog

All notable changes to the HR Phone Extension Management module will be documented in this file.

## [17.0.1.0.0] - 2024-11-22

### Changed
- Migrated module to Odoo 17.0
- Updated `view_mode` from `tree,form` to `list,form` in actions
- Updated `binding_view_types` from `form,tree` to `list,form` in server actions
- Updated `_name_search` method signature (changed `name_get_uid` to `order` parameter)
- Maintained backward compatibility with all existing features

### Technical
- Built for Odoo 17.0
- All dependencies remain compatible
- No breaking changes to data structure

## [16.0.1.0.0] - 2024-11-20

### Added
- Initial release of HR Phone Extension Management module
- Centralized phone extension management system
- Phone Extension model (`hr.phone.extension`) with the following fields:
  - Extension number
  - Employee assignment
  - Department tracking
  - Location/office information
  - Notes and description
- Integration with HR Employee model
- Bi-directional linking between extensions and employees
- Extension field added to employee profiles (`hr.employee`)
- Extension information in public employee views (`hr.employee.public`)
- Dedicated menu structure for extension management
- Security access rules (ir.model.access.csv)
- Multiple view types:
  - Tree (list) view for extensions
  - Form view for extension details
  - Kanban view for visual management
  - Search view with filters and grouping
- Mail/Chatter integration for activity tracking
- Employee form view enhancements showing extension information

### Features
- Create and manage phone extensions
- Assign extensions to employees
- Track extension availability
- View extensions by department
- Search and filter extensions
- Integration with employee records
- Activity logging and notes

### Technical
- Initial release for Odoo 16.0
- Depends on: base, hr, mail modules
- License: OPL-1 (Odoo Proprietary License)
- Category: Human Resources
- Application module

### Documentation
- Complete README.md with usage instructions
- Comprehensive module description
- Installation guide
- Configuration steps

---

## Future Versions

### Planned Features
- VOIP integration
- Call logging and history
- Extension availability scheduling
- SMS/email notifications
- Extension transfer functionality
- Call forwarding rules
- Integration with external phone systems
- Mobile app support
- Analytics and reporting
- Extension groups/teams
- Auto-assignment rules

---

**Author:** Technology Pill Business Solution  
**Contact:** admin@tecpill.com  
**Website:** https://www.tecpill.com/
