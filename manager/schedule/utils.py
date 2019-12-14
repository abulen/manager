from calendar import HTMLCalendar
from datetime import datetime as dtime, date, time
import datetime
from django.db.models import Q
from .models import Shift
from .models import SSW
from .models import Leave


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
            shifts_html += shift.get_absolute_url() + "<br>"
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
        #cal_html = "<ul>"
        cal_html = ""
        for ssw in ssws_from_day:
            cal_html += ssw.get_absolute_url() + "<br>"
            css_classes += " ssw-day"
        for leave in leaves_from_day:
            cal_html += leave.get_absolute_url() + "<br>"
        for shift in shifts_from_day:
            cal_html += shift.get_absolute_url() + "<br>"
        #cal_html += "</ul>"

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
