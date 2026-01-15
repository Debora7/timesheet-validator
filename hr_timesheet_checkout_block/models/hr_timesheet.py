from odoo import models

class HrTimesheet(models.Model):
    _inherit = "account_analytic_line"

    def create(self, vals_list):