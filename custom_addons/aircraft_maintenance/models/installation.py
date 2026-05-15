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

    def install(self, aircraft):
        for comp in self:

            # close previous installation if exists
            active_install = self.env[
                "aircraft.component.installation"
            ].search([
                ("component_id", "=", comp.id),
                ("is_active", "=", True)
            ], limit=1)

            if active_install:
                active_install.write({
                    "removed_at": fields.Datetime.now(),
                    "is_active": False
                })

            # create new installation record
            self.env["aircraft.component.installation"].create({
                "component_id": comp.id,
                "aircraft_id": aircraft.id,
                "installed_at": fields.Datetime.now(),
                "is_active": True
            })

            comp.aircraft_id = aircraft.id
            comp.is_installed = True

    def uninstall(self):
        for comp in self:

            active_install = self.env[
                "aircraft.component.installation"
            ].search([
                ("component_id", "=", comp.id),
                ("is_active", "=", True)
            ], limit=1)

            if active_install:
                active_install.write({
                    "removed_at": fields.Datetime.now(),
                    "is_active": False
                })

            comp.aircraft_id = False
            comp.is_installed = False