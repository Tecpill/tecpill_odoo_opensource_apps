# -*- coding: utf-8 -*-

import json
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    log_cleanup_enabled = fields.Boolean(
        string='Log Cleanup Enabled',
        default=False,
        help='Enable automated log cleanup via scheduled action'
    )
    
    rotation_mode = fields.Selection(
        [
            ('time', 'Time-Based Rotation'),
            ('count', 'Count-Based Rotation'),
        ],
        string='Rotation Mode',
        default='time',
        config_parameter='logging_cleanup.rotation_mode',
        help='Select the rotation strategy for log cleanup'
    )
    
    log_retention_days = fields.Integer(
        string='Default Log Retention Days',
        default=30,
        config_parameter='logging_cleanup.log_retention_days',
        help='Default retention period for logs (days)'
    )
    
    rotation_max_records = fields.Integer(
        string='Max Records to Keep (Count Mode)',
        default=100000,
        config_parameter='logging_cleanup.rotation_max_records',
        help='Maximum number of log records to keep in count-based rotation mode'
    )
    
    log_level_retention_rules = fields.Text(
        string='Log Level Retention Rules (JSON)',
        default='''{
    "DEBUG": 3,
    "INFO": 7,
    "WARNING": 30,
    "ERROR": 90,
    "CRITICAL": 180
}''',
        help='JSON configuration for retention days per log level. Format: {"LEVEL": days}'
    )

    def set_values(self):
        icp = self.env['ir.config_parameter'].sudo()
        
        # Call super to save all other config parameters first
        super(ResConfigSettings, self).set_values()
        
        # Explicitly save the Boolean field to ensure False is stored correctly
        # Store as string "True" or "False"
        icp.set_param('logging_cleanup.log_cleanup_enabled', str(self.log_cleanup_enabled))
        
        # After saving, check if log_cleanup_enabled is now False
        if not self.log_cleanup_enabled:
            # Clear all logging_cleanup config parameters by deleting them
            config_params_to_clear = [
                'logging_cleanup.rotation_mode',
                'logging_cleanup.log_retention_days',
                'logging_cleanup.rotation_max_records',
                'logging_cleanup.log_level_retention_rules',
            ]
            for param_key in config_params_to_clear:
                # Delete the config parameter completely
                icp.search([('key', '=', param_key)]).unlink()
        else:
            # If enabled is True, restore/re-create all config parameters from field values
            # Validate and save JSON format for log_level_retention_rules
            if self.log_level_retention_rules:
                try:
                    # Validate JSON
                    parsed_json = json.loads(self.log_level_retention_rules)
                    
                    # Validate structure: must be a dictionary
                    if not isinstance(parsed_json, dict):
                        raise UserError(_('Log Level Retention Rules must be a JSON object (dictionary), not a %s') % type(parsed_json).__name__)
                    
                    # Validate values: must be positive integers
                    for level, days in parsed_json.items():
                        if not isinstance(days, int) or days < 1:
                            raise UserError(_('Retention days for level "%s" must be a positive integer, got: %s') % (level, days))
                    
                    # Save to config parameter
                    icp.set_param(
                        'logging_cleanup.log_level_retention_rules',
                        self.log_level_retention_rules
                    )
                except (ValueError, TypeError) as e:
                    raise UserError(_('Invalid JSON format in Log Level Retention Rules: %s') % str(e))
            # Other parameters are already saved by super() through their config_parameter attribute

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        # Get the JSON config from parameter if not set
        icp = self.env['ir.config_parameter'].sudo()
        
        # Explicitly get and convert the Boolean field
        cleanup_enabled_str = icp.get_param('logging_cleanup.log_cleanup_enabled', 'False')
        res['log_cleanup_enabled'] = cleanup_enabled_str.lower() == 'true' if cleanup_enabled_str else False
        
        retention_rules = icp.get_param(
            'logging_cleanup.log_level_retention_rules',
            '{"DEBUG": 3, "INFO": 7, "WARNING": 30, "ERROR": 90, "CRITICAL": 180}'
        )
        res.update({
            'log_level_retention_rules': retention_rules,
        })
        return res

    @api.model
    def get_retention_rules(self):
        """Get retention rules as a dictionary"""
        icp = self.env['ir.config_parameter'].sudo()
        retention_json = icp.get_param(
            'logging_cleanup.log_level_retention_rules',
            '{"DEBUG": 3, "INFO": 7, "WARNING": 30, "ERROR": 90, "CRITICAL": 180}'
        )
        try:
            return json.loads(retention_json)
        except (ValueError, TypeError):
            return {"DEBUG": 3, "INFO": 7, "WARNING": 30, "ERROR": 90, "CRITICAL": 180}

    def action_clean_logs_now(self):
        """Manual cleanup action from settings"""
        self.ensure_one()
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_('Only users with Technical Settings access can perform log cleanup.'))
        
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

