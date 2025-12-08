# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    extension_id = fields.Many2one(
        'phone.extension',
        string='Phone Extension',
        help='Internal phone extension assigned to this employee'
    )
    extension_number = fields.Char(
        string='Extension Number',
        related='extension_id.number',
        store=True,
        readonly=True,
        help='Extension number for quick search'
    )

    @api.onchange('department_id')
    def _onchange_department_id(self):
        """Suggest department extension when department changes"""
        if self.department_id:
            domain = [('department_id', '=', self.department_id.id), ('active', '=', True)]
            extension = self.env['phone.extension'].search(domain, limit=1)
            if extension:
                self.extension_id = extension

