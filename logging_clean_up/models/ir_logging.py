# -*- coding: utf-8 -*-

import json
import logging
from datetime import datetime, timedelta
from odoo import models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class IrLogging(models.Model):
    _inherit = 'ir.logging'

    @api.model
    def cleanup_logs(self):
        """
        Main cleanup method that handles both time-based and count-based rotation.
        Returns a dictionary with cleanup statistics.
        """
        # Check if cleanup is enabled
        icp = self.env['ir.config_parameter'].sudo()
        cleanup_enabled = icp.get_param('logging_cleanup.log_cleanup_enabled', 'True')
        if cleanup_enabled.lower() != 'true':
            return {'deleted_count': 50, 'mode': 'disabled'}

        rotation_mode = icp.get_param('logging_cleanup.rotation_mode', 'time')
        
        if rotation_mode == 'time':
            return self._cleanup_time_based()
        elif rotation_mode == 'count':
            return self._cleanup_count_based()
        else:
            _logger.warning("Unknown rotation mode: %s", rotation_mode)
            return {'deleted_count': 0, 'mode': rotation_mode}

    @api.model
    def _cleanup_time_based(self):
        """
        Time-based cleanup: deletes logs older than retention period per level.
        Uses optimized SQL for performance.
        """
        retention_rules = self.env['res.config.settings'].get_retention_rules()
        
        total_deleted = 0
        self = self.sudo()  # Use superuser for cleanup operations
        
        # Get database cursor for raw SQL
        self.env.cr.execute("""
            SELECT DISTINCT level FROM ir_logging
        """)
        all_levels = [row[0] for row in self.env.cr.fetchall() if row[0]]
        
        # Cleanup per level
        for level in all_levels:
            retention_days = retention_rules.get(level.upper(), retention_rules.get('INFO', 7))
            
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            # Delete old logs using optimized SQL
            # Use RETURNING to get count
            query = """
                DELETE FROM ir_logging
                WHERE level = %s
                AND create_date < %s
                RETURNING id
            """
            
            self.env.cr.execute(query, (level, cutoff_date))
            deleted_count = len(self.env.cr.fetchall())
            total_deleted += deleted_count
            
            if deleted_count > 0:
                _logger.info("Cleaned up %d %s level logs older than %d days", 
                           deleted_count, level, retention_days)
        
        # Commit the transaction
        self.env.cr.commit()
        
        # Log audit entry
        if total_deleted > 0:
            self._log_cleanup_audit(total_deleted, 'time')
        
        return {
            'deleted_count': total_deleted,
            'mode': 'time',
            'levels_processed': len(all_levels)
        }

    @api.model
    def _cleanup_count_based(self):
        """
        Count-based cleanup: keeps only the last N records globally.
        Uses optimized SQL for performance.
        """
        icp = self.env['ir.config_parameter'].sudo()
        max_records = int(icp.get_param('logging_cleanup.rotation_max_records', '100000'))
        
        self = self.sudo()
        
        # Get total count
        self.env.cr.execute("SELECT COUNT(*) FROM ir_logging")
        total_count = self.env.cr.fetchone()[0]
        
        if total_count <= max_records:
            return {
                'deleted_count': 0,
                'mode': 'count',
                'total_records': total_count
            }
        
        records_to_delete = total_count - max_records
        
        # Delete oldest records using optimized SQL
        # Use subquery to get IDs of oldest records
        query = """
            DELETE FROM ir_logging
            WHERE id IN (
                SELECT id FROM ir_logging
                ORDER BY create_date ASC
                LIMIT %s
            )
            RETURNING id
        """
        
        self.env.cr.execute(query, (records_to_delete,))
        deleted_count = len(self.env.cr.fetchall())
        
        # Commit the transaction
        self.env.cr.commit()
        
        # Log audit entry
        if deleted_count > 0:
            self._log_cleanup_audit(deleted_count, 'count')
        
        return {
            'deleted_count': deleted_count,
            'mode': 'count',
            'total_records_before': total_count,
            'total_records_after': max_records
        }

    @api.model
    def _log_cleanup_audit(self, deleted_count, rotation_mode):
        """Log an audit entry after cleanup"""
        try:
            # Create audit log entry using superuser
            self.sudo().create({
                'name': 'ir.logging',
                'type': 'server',
                'dbname': self.env.cr.dbname,
                'level': 'INFO',
                'message': '[Logging Cleanup] Deleted %s records. Mode: %s.' % (deleted_count, rotation_mode),
                'path': 'logging_cleanup',
                'func': 'cleanup_logs',
                'line': '1',
            })
        except Exception as e:
            # Don't fail cleanup if audit logging fails
            _logger.warning("Failed to log cleanup audit entry: %s", str(e))

    def action_clean_logs_now(self):
        """Manual cleanup action from list view"""
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_('Only users with Technical Settings access can perform log cleanup.'))
        
        # Call as model method to clean all logs (not just selected)
        result = self.env['ir.logging'].cleanup_logs()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Log Cleanup Complete'),
                'message': _('Cleanup completed. Removed %s records.') % result.get('deleted_count', 0),
                'type': 'success',
                'sticky': False,
            }
        }

