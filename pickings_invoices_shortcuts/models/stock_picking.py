# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # Smart button fields for what's missing
    invoice_count = fields.Integer(
        string="Invoice Count",
        compute='_compute_invoice_count'
    )
    invoice_ids = fields.Many2many(
        'account.move',
        string="Invoices",
        compute='_compute_invoice_count'
    )

    @api.depends('sale_id.invoice_ids')
    def _compute_invoice_count(self):
        """Compute invoice count and ids for smart button."""
        for picking in self:
            invoices = self.env['account.move']
            
            # Get invoices from related sale order (leveraging existing sale_id field from sale_stock)
            if picking.sale_id:
                invoices = picking.sale_id.invoice_ids.filtered(
                    lambda inv: inv.move_type in ('out_invoice', 'out_refund') and inv.state != 'cancel'
                )
            
            picking.invoice_ids = invoices
            picking.invoice_count = len(invoices)

    def action_view_sale_order(self):
        """Action to view related sale order (smart button version of existing sale_id field)."""
        self.ensure_one()
        
        if not self.sale_id:
            return {'type': 'ir.actions.act_window_close'}
        
        return {
            'name': 'Sale Order',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.sale_id.id,
            'context': {'create': False}
        }

    def action_view_invoice(self):
        """Action to view related invoices."""
        self.ensure_one()
        
        invoices = self.invoice_ids
        
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_out_invoice_type')
        
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        # Properly handle context - prevent RPC errors
        context = {
            'default_move_type': 'out_invoice',
            'create': False,
        }
        if isinstance(action.get('context'), dict):
            action['context'].update(context)
        else:
            action['context'] = context
        
        return action 