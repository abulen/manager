from calendar import HTMLCalendar
from datetime import datetime as dtime, date, time
import datetime
from django.db.models import Q
from .models import Shift
from .models import SSW
from .models import Leave
from employee.models import Employee


class ShiftCalendar(HTMLCalendar):
    def __init__(self, shifts=None):
        super().__init__()
        self.setfirstweekday(6)
        self.shifts = shifts

    def formatday(self, day, weekday, shifts):
        """
        Return a day as a table cell.
        """
        shifts_from_day = shifts.filter(date__day=day).order_by('start')
        shifts_html = "<ul>"
        for shift in shifts_from_day:
            shifts_html += shift.get_calendar_url() + "<br>"
        shifts_html += "</ul>"

        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        else:
            return '<td class="%s">%d%s</td>' % (
            self.cssclasses[weekday], day, shifts_html)

    def formatweek(self, theweek, shifts):
        """
        Return a complete week as a table row.
        """
        s = ''.join(self.formatday(d, wd, shifts) for (d, wd) in theweek)
        return '<tr>%s</tr>' % s

    def formatmonth(self, theyear, themonth, withyear=True):
        """
        Return a formatted month as a table.
        """

        shifts = Shift.objects.filter(date__month=themonth)

        v = []
        a = v.append
        a('<table border="0" cellpadding="0" cellspacing="0" class="month">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week, shifts))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)


class ScheduleCalendar(HTMLCalendar):
    def __init__(self, shifts=None, ssws=None, leaves=None):
        super().__init__()
        self.setfirstweekday(6)
        self.shifts = shifts
        self.ssws = ssws
        self.leaves = leaves

    def formatday(self, day, weekday, shifts, ssws, leaves):
        """
        Return a day as a table cell.
        """
        ssws_from_day = ssws.filter(date__day=day)
        leaves_from_day = leaves.filter(date__day=day)
        shifts_from_day = shifts.filter(date__day=day).order_by('start')
        css_classes = self.cssclasses[weekday]
        cal_html = ""
        for ssw in ssws_from_day:
            cal_html += ssw.get_calendar_url() + "<br>"
            css_classes += " ssw-day"
        for leave in leaves_from_day:
            cal_html += leave.get_calendar_url() + "<br>"
        for shift in shifts_from_day:
            cal_html += shift.get_calendar_url() + "<br>"

        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        else:
            return '<td class="%s">%d%s</td>' % (
                css_classes, day, cal_html)

    def formatweek(self, theweek, shifts, ssws, leaves):
        """
        Return a complete week as a table row.
        """
        s = ''.join(self.formatday(d, wd, shifts, ssws, leaves) for
                    (d, wd) in theweek)
        return '<tr>%s</tr>' % s

    def formatmonth(self, theyear, themonth, withyear=True):
        """
        Return a formatted month as a table.
        """

        shifts = Shift.objects.filter(date__month=themonth)
        ssws = SSW.objects.filter(date__month=themonth)
        leaves = Leave.objects.filter(date__month=themonth)

        v = []
        a = v.append
        a('<table border="0" cellpadding="0" cellspacing="0" class="month">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week, shifts, ssws, leaves))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)


class ScheduleTable:

    def get_week(self, sunday):
        week = dict()
        week['sunday'] = sunday
        week['monday'] = sunday + datetime.timedelta(days=1)
        week['tuesday'] = sunday + datetime.timedelta(days=2)
        week['wednesday'] = sunday + datetime.timedelta(days=3)
        week['thursday'] = sunday + datetime.timedelta(days=4)
        week['friday'] = sunday + datetime.timedelta(days=5)
        week['saturday'] = sunday + datetime.timedelta(days=6)
        return week

    def format_employee_day(self, shift):
        html = "<td>"
        if shift:
            html += "{} - {}".format(
                shift.start.strftime("%I:%M"),
                shift.end.strftime("%I:%M"))
        else:
            html += "off"
        html += "</td>"
        return html

    def format_employee_week(self, emp, shifts, week):
        emp_shifts = shifts.filter(employee=emp)
        html = "<tr><td>{} {}</td>".format(
            emp.user.first_name,
            emp.user.last_name
        )
        for day in week:
            shift_qs = emp_shifts.filter(date=week[day])
            if shift_qs.exists():
                shift = shift_qs.first()
            else:
                shift = None
            html += self.format_employee_day(shift)
        html += "</tr>"
        return html

    def format_week(self, sunday):
        saturday = sunday + datetime.timedelta(days=6)
        shifts = Shift.objects.filter(
            Q(date__gte=sunday),
            Q(date__lte=saturday)
        )
        week = self.get_week(sunday)
        employees = Employee.objects.active().order_by('user__last_name')
        header = "<table class='table table-striped'>" + \
                 "<thead class='thead-dark'><tr><th>Employee</th>"
        for day_name in week.keys():
            day = week[day_name]
            header += "<th>"
            header += "{}<br>{}/{}".format(
                day_name.capitalize(),
                day.month,
                day.day)
            header += "</th>"
        header += "</tr></thead><tbody>"

        s = ''.join(self.format_employee_week(emp, shifts, week) for
                    emp in employees)
        return header + s + "</tbody></table>"

