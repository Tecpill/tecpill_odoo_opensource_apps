# -*- coding: utf-8 -*-

from odoo import models, fields


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    extension_id = fields.Many2one(
        'phone.extension',
        string='Phone Extension',
        readonly=True
    )
    extension_number = fields.Char(
        string='Extension Number',
        related='extension_id.number',
        readonly=True,
        help='Extension number for quick search'
    )

