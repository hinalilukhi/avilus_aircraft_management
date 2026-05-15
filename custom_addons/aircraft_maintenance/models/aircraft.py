from odoo import models, fields

class Aircraft(models.Model):
    _name = "aircraft.aircraft"
    _description = "Aircraft"

    name = fields.Char(required=True)

    code = fields.Char(string="Aircraft Code")

    active = fields.Boolean(default=True)