from odoo import models, fields
import logging
from datetime import datetime
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    procent = fields.Float(store=True)
    working_hours = fields.Boolean(store=True)
    attendance = fields.Boolean(store=True)

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

        if self.working_hours:
            self.with_context(to_check='working_hours').timesheet_restriction(total_hours_spent)

        if self.attendance:
            self.with_context(to_check='attendance').timesheet_restriction(total_hours_spent)

        if(len(timesheets) == 0 and len(attendance_status) != 0):
           raise UserError("User has no timesheet entries for today.")

        super()._attendance_action_change(geo_information=geo_information)

        return True

    def timesheet_restriction(self, total_hours_spent):
        context = self.env.context['to_check']

        if context == 'working_hours':
            working_hours = self.resource_calendar_id.hours_per_day

        if context == 'attendance':
            working_hours = 0
            attendance = self.attendance_ids.filtered(lambda l : l.date.strftime("%Y-%m-%d") == datetime.today().strftime("%Y-%m-%d"))
            
            for att in attendance:
                working_hours = working_hours + att.worked_hours

        if total_hours_spent < working_hours * self.procent:
            raise UserError(f"User has only {total_hours_spent} hours logged. It should be {working_hours} hours.")