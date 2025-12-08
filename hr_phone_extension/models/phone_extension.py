# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PhoneExtension(models.Model):
    _name = 'phone.extension'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Phone Extension'
    _order = 'number'
    _rec_name = 'number'

    number = fields.Char(
        string='Extension Number',
        required=True,
        index=True,
        tracking=True,
        help='Internal phone extension number (must be unique)'
    )
    employee_ids = fields.One2many(
        'hr.employee',
        'extension_id',
        string='Assigned Employees',
    )
    employee_count = fields.Integer(
        string='Employee Count',
        compute='_compute_employee_count',
        store=False
    )
    number_range = fields.Char(
        string='Extension Range',
        compute='_compute_number_range',
        store=True,
        index=True,
        tracking=True,
        help='First digit of extension number for grouping'
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        tracking=True,
        help='Department this extension is primarily assigned to'
    )
    notes = fields.Text(
        string='Notes',
        tracking=True,
        help='IT notes or troubleshooting information'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True,
        help='Archive unused extensions'
    )

    _sql_constraints = [
        ('number_unique', 'unique(number)', 'Extension number must be unique!')
    ]

    def _compute_employee_count(self):
        for record in self:
            record.employee_count = len(record.employee_ids)

    @api.depends('number')
    def _compute_number_range(self):
        for record in self:
            if record.number and record.number[0].isdigit():
                record.number_range = f"{record.number[0]}xx"
            else:
                record.number_range = False

    @api.model
    def create(self, vals):
        """Override create to add employee from context if provided"""
        if 'default_from_employee_id' in self.env.context:
            employee_id = self.env.context.get('default_from_employee_id')
            if employee_id and 'employee_ids' not in vals:
                vals['employee_ids'] = [(4, employee_id)]
        return super(PhoneExtension, self).create(vals)

    def name_get(self):
        result = []
        for record in self:
            name = record.number if record.number else 'New Extension'
            result.append((record.id, name))
        return result

    def action_assign_department(self):
        """Server action: Assign Department

        For each phone extension record, if it has linked employees and they
        all belong to the same department, assign that department to the
        extension. If employees belong to multiple departments or there are
        no employees, clear the department on the extension.
        """
        _logger = logging.getLogger(__name__)
        for record in self:
            _logger.info('Assign Department called for phone.extension id=%s number=%s', record.id, record.number)
            if record.employee_ids:
                # Collect all unique department IDs from linked employees
                employee_depts = record.employee_ids.mapped('department_id')
                dept_ids = set(employee_depts.ids)
                _logger.debug('  linked employee ids: %s', record.employee_ids.ids)
                _logger.debug('  linked employee department ids: %s', list(dept_ids))
                if len(dept_ids) == 1:
                    # All employees share the same department → assign it safely
                    dept_id = list(dept_ids)[0]
                    _logger.info('  assigning department_id=%s to phone.extension id=%s', dept_id, record.id)
                    record.write({'department_id': dept_id})
                else:
                    # Employees belong to different departments → clear department
                    _logger.warning('  multiple departments found (%s) - clearing department for phone.extension id=%s', list(dept_ids), record.id)
                    record.write({'department_id': False})
            else:
                # No employees assigned → clear department
                _logger.info('  no employees assigned - clearing department for phone.extension id=%s', record.id)
                record.write({'department_id': False})

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = [('number', operator, name)]
        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)
