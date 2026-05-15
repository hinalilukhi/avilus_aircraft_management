from odoo import models, fields
from odoo.exceptions import ValidationError


class AircraftFinding(models.Model):
    _name = "aircraft.finding"
    _description = "Aircraft Finding / Technical Log Entry"

    name = fields.Char(required=True)

    description = fields.Text()

    is_tle = fields.Boolean(
        string="Technical Log Entry (TLE)",
        default=False
    )

    def unlink(self):
        for rec in self:
            if rec.is_tle:
                raise ValidationError(
                    "This record is marked as Technical Log Entry (TLE) "
                    "and cannot be deleted."
                )

        return super().unlink()