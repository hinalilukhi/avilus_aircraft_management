from odoo import models, fields, api


class FlightLog(models.Model):
    _name = "aircraft.flight.log"
    _description = "Aircraft Flight Log"

    aircraft_id = fields.Many2one(
        "aircraft.aircraft",
        required=True
    )

    flight_hours = fields.Float(required=True)
    cycles = fields.Integer(required=True)

    flight_date = fields.Datetime(default=fields.Datetime.now)

    is_emergency = fields.Boolean(
        string="Emergency Flight",
        default=False
    )

    # ---------------------------------
    # CREATE
    # ---------------------------------
    @api.model
    def create(self, vals):

        record = super().create(vals)
        record._process_flight()
        return record

    # ---------------------------------
    # WRITE (IMPORTANT FIX)
    # ---------------------------------
    def write(self, vals):
        res = super().write(vals)
        self._process_flight()
        return res

    # ---------------------------------
    # CORE LOGIC (REUSED)
    # ---------------------------------
    def _process_flight(self):
        for record in self:

            if not record.aircraft_id:
                continue

            # find all installed components on this aircraft
            components = self.env["aircraft.component"].search([
                ("aircraft_id", "=", record.aircraft_id.id),
                ("is_installed", "=", True)
            ])

            # update each component
            for comp in components:
                comp.total_hours += record.flight_hours
                comp.total_cycles += record.cycles

                # recompute maintenance status
                comp.calculate_next_due()

            # ---------------------------------
            # AUTO CREATE FINDING
            # ---------------------------------
            if record.is_emergency:

                existing = self.env["aircraft.finding"].search([
                    ("name", "=", f"Emergency Flight - {record.aircraft_id.name}")
                ], limit=1)

                if not existing:
                    self.env["aircraft.finding"].create({
                        "name": f"Emergency Flight - {record.aircraft_id.name}",
                        "description": (
                            f"Emergency flight detected on aircraft "
                            f"{record.aircraft_id.name}"
                        ),
                        "is_tle": True
                    })