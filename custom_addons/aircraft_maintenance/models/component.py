from odoo import models, fields, api
from datetime import timedelta


class Component(models.Model):
    _name = "aircraft.component"
    _description = "Aircraft Component (LRU)"

    name = fields.Char(required=True)

    # lifecycle tracking
    total_hours = fields.Float(default=0.0)
    total_cycles = fields.Integer(default=0)

    # installation state
    is_installed = fields.Boolean(default=False)

    aircraft_id = fields.Many2one(
        "aircraft.aircraft",
        string="Current Aircraft"
    )

    # maintenance tracking
    last_service_date = fields.Date()

    # computed next due outputs
    next_due_date = fields.Date()
    next_due_hours = fields.Float()
    next_due_cycles = fields.Integer()

    # -----------------------------
    # CORE METHOD: next due logic
    # -----------------------------
    def calculate_next_due(self):
        for comp in self:

            # 1. Calendar rule (24 months)
            calendar_due = False
            if comp.last_service_date:
                calendar_due = comp.last_service_date + timedelta(days=24 * 30)

            # 2. Utilization rules
            hours_due = max(0, 3000 - comp.total_hours)
            cycles_due = max(0, 1500 - comp.total_cycles)

            comp.next_due_date = calendar_due
            comp.next_due_hours = hours_due
            comp.next_due_cycles = cycles_due

        return True
    
    def write(self, vals):

        old_values = {rec.id: rec.is_installed for rec in self}

        res = super().write(vals)

        for rec in self:

            old = old_values[rec.id]
            new = rec.is_installed

            # ---------------------------------
            # INSTALLATION EVENT
            # ---------------------------------
            if not old and new:
                self.env["aircraft.component.installation"].create({
                    "component_id": rec.id,
                    "aircraft_id": rec.aircraft_id.id,
                    "installed_at": fields.Datetime.now(),
                    "is_active": True
                })

            # ---------------------------------
            # UNINSTALLATION EVENT
            # ---------------------------------
            if old and not new:

                history = self.env["aircraft.component.installation"].search([
                    ("component_id", "=", rec.id),
                    ("is_active", "=", True)
                ], limit=1)

                if history:
                    history.write({
                        "removed_at": fields.Datetime.now(),
                        "is_active": False
                    })

        return res

