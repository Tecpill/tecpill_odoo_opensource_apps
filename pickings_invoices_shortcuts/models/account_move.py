# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Smart button field for pickings (new functionality)
    picking_count = fields.Integer(
        string="Picking Count",
        compute='_compute_picking_count'
    )
    picking_ids = fields.Many2many(
        'stock.picking',
        string="Pickings",
        compute='_compute_picking_count'
    )

    @api.depends('line_ids.sale_line_ids.order_id')
    def _compute_picking_count(self):
        """Compute picking count and ids for smart button."""
        for move in self:
            pickings = self.env['stock.picking']
            
            # Get pickings from related sale orders (leveraging existing sale_line_ids relationship)
            sale_orders = move.line_ids.sale_line_ids.order_id
            for sale_order in sale_orders:
                # Use the existing delivery functionality from sale_stock
                if hasattr(sale_order, 'picking_ids'):
                    pickings |= sale_order.picking_ids.filtered(lambda p: p.state != 'cancel')
            
            move.picking_ids = pickings
            move.picking_count = len(pickings)

    def action_view_picking(self):
        """Action to view related pickings (new functionality)."""
        self.ensure_one()
        
        pickings = self.picking_ids
        
        action = self.env['ir.actions.act_window']._for_xml_id('stock.action_picking_tree_all')
        
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif len(pickings) == 1:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = pickings.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        # Properly handle context - fix for the RPC error
        context = {'create': False}
        if isinstance(action.get('context'), dict):
            action['context'].update(context)
        else:
            action['context'] = context
        
        return action 