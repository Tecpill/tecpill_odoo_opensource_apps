# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.exceptions import AccessError


class ResUsers(models.Model):
    _inherit = 'res.users'

    # Copied from sign module; keep in sync if Sign adds attributes (e.g., attachment=True, sanitize, etc.)
    sign_signature = fields.Binary(string="Digital Signature", copy=False, groups="base.group_user")
    sign_initials = fields.Binary(string="Digitial Initials", copy=False, groups="base.group_user")

    @property
    def SELF_WRITEABLE_FIELDS(self):
        """Extend base writable fields to include signature fields"""
        return super().SELF_WRITEABLE_FIELDS + ['sign_signature', 'sign_initials']

    def write(self, vals):
        # Admins: unchanged behavior
        if self.env.user.has_group('base.group_system'):
            return super().write(vals)

        signature_fields = {'sign_signature', 'sign_initials'}
        is_signature_context = bool(self.env.context.get('user_sign_profile_only'))
        keys = set(vals.keys())
        touching_signature = bool(signature_fields & keys)

        # Only enforce extra rules when signature is involved (or context explicitly requests strictness)
        if is_signature_context or touching_signature:
            # Non-admins can only edit their own user record for signature updates
            if any(u.id != self.env.uid for u in self):
                raise AccessError(_("You can only edit your own digital signature/initials."))

            # In signature context, block editing anything else
            if is_signature_context:
                extra = keys - signature_fields
                if extra:
                    raise AccessError(_("You can only edit signature fields here."))

        return super().write(vals)
