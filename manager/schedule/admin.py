from django.contrib import admin
from . import models
# Register your models here.
import datetime
import calendar
from django.urls import reverse
from .utils import ShiftCalendar
from calendar import HTMLCalendar
from django.utils.safestring import mark_safe


@admin.register(models.Leave)
class LeaveAdmin(admin.ModelAdmin):
    pass


@admin.register(models.SSW)
class SSWAdmin(admin.ModelAdmin):
    pass


class ShiftAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'start', 'end', 'employee']
    change_list_template = 'admin/shifts/change_list.html'

    def changelist_view(self, request, extra_context=None):
        after_day = request.GET.get('date__gte', None)
        extra_context = extra_context or {}

        if not after_day:
            d = datetime.date.today()
        else:
            try:
                split_after_day = after_day.split('-')
                d = datetime.date(year=int(split_after_day[0]),
                                  month=int(split_after_day[1]), day=1)
            except:
                d = datetime.date.today()

        previous_month = datetime.date(year=d.year, month=d.month,
                                       day=1)  # find first day of current month
        previous_month = previous_month - datetime.timedelta(
            days=1)  # backs up a single day
        previous_month = datetime.date(year=previous_month.year,
                                       month=previous_month.month,
                                       day=1)  # find first day of previous month

        last_day = calendar.monthrange(d.year, d.month)
        next_month = datetime.date(year=d.year, month=d.month, day=last_day[
            1])  # find last day of current month
        next_month = next_month + datetime.timedelta(
            days=1)  # forward a single day
        next_month = datetime.date(year=next_month.year, month=next_month.month,
                                   day=1)  # find first day of next month

        extra_context['previous_month'] = reverse(
            'admin:schedule_shift_changelist') + '?date__gte=' + str(
            previous_month)
        extra_context['next_month'] = reverse(
            'admin:schedule_shift_changelist') + '?date__gte=' + str(next_month)

        cal = ShiftCalendar()
        html_calendar = cal.formatmonth(d.year, d.month, withyear=True)
        html_calendar = html_calendar.replace('<td ',
                                              '<td  width="150" height="150"')
        extra_context['calendar'] = mark_safe(html_calendar)
        return super().changelist_view(request, extra_context)


admin.site.register(models.Shift, ShiftAdmin)


@admin.register(models.GoogleCalendar)
class GoogleCalendarAdmin(admin.ModelAdmin):
    pass
