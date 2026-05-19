from odoo import models, fields


class ComponentInstallation(models.Model):
    _name = "aircraft.component.installation"
    _description = "Component Installation History"

    component_id = fields.Many2one(
        "aircraft.component",
        required=True,
        ondelete="cascade"
    )

    aircraft_id = fields.Many2one(
        "aircraft.aircraft",
        required=True
    )

    installed_at = fields.Datetime(
        default=fields.Datetime.now,
        required=True
    )

    removed_at = fields.Datetime()

    is_active = fields.Boolean(default=True)

