from odoo import models
import logging
from datetime import datetime
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _attendance_action_change(self, geo_information = None):
        current_user_id = self.env.user.id
        current_date = datetime.today().strftime("%Y-%m-%d")
        attendance_status = self.env["hr.attendance"].search([
            ("employee_id" ,"=", self.id),
            ("check_in", ">=", current_date),
            ("check_out", "=", False), 
        ])

        timesheets = self.env['account.analytic.line'].search([
            ("user_id", "=", current_user_id),
            ("date", "=", current_date),
            ("unit_amount" , ">", 0),
        ])

        total_hours_spent = 0
        for time in timesheets:
            total_hours_spent += time.unit_amount

        working_hours = self.resource_calendar_id.hours_per_day

        if total_hours_spent < working_hours * 0.8:
            raise UserError(f"User has only {total_hours_spent} hours logged. It should be {working_hours} hours.")

        if(len(timesheets) == 0 and len(attendance_status) != 0):
           raise UserError("User has no timesheet entries for today.")

        super()._attendance_action_change(geo_information=geo_information)

        return True
