from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Shift
from .models import SSW
from .models import Leave
from schedule import tasks
from .utils import ScheduleCalendar
from .utils import ScheduleTable
from . import forms
from datetime import timedelta
from datetime import date
import calendar
from django.http import JsonResponse


class CalendarIndexView(View):
    def get(self, request, *args, **kwargs):
        context = self.get_context_date(request)
        return render(request, 'schedule/calendar.html', context=context)

    def get_context_date(self, request, context=None):
        after_day = request.GET.get('date__gte', None)
        context = context or {}

        if not after_day:
            d = date.today()
        else:
            try:
                split_after_day = after_day.split('-')
                d = date(year=int(split_after_day[0]),
                                  month=int(split_after_day[1]), day=1)
            except:
                d = date.today()

        previous_month = date(year=d.year, month=d.month,
                                       day=1)  # find first day of current month
        previous_month = previous_month - timedelta(
            days=1)  # backs up a single day
        previous_month = date(year=previous_month.year,
                                       month=previous_month.month,
                                       day=1)  # find first day of previous month

        last_day = calendar.monthrange(d.year, d.month)
        next_month = date(year=d.year, month=d.month, day=last_day[
            1])  # find last day of current month
        next_month = next_month + timedelta(
            days=1)  # forward a single day
        next_month = date(year=next_month.year, month=next_month.month,
                                   day=1)  # find first day of next month

        context['previous_month'] = reverse(
            'schedule:calendar-index') + '?date__gte=' + str(
            previous_month)
        context['next_month'] = reverse(
            'schedule:calendar-index') + '?date__gte=' + str(next_month)

        cal = ScheduleCalendar()
        html_calendar = cal.formatmonth(d.year, d.month, withyear=True)
        html_calendar = html_calendar.replace('<td ',
                                              '<td  width="150" height="150"')
        context['calendar'] = mark_safe(html_calendar)
        return context


class ScheduleView(View):
    def get(self, request, *args, **kwargs):
        context = self.get_context_date(request)
        return render(request, 'schedule/schedule.html', context=context)

    def get_context_date(self, request, context=None):
        after_day = request.GET.get('date__gte', None)
        context = context or {}

        if not after_day:
            d = date.today()
        else:
            try:
                split_after_day = after_day.split('-')
                d = date(year=int(split_after_day[0]),
                                  month=int(split_after_day[1]), day=1)
            except:
                d = date.today()

        previous_month = date(year=d.year, month=d.month,
                                       day=1)  # find first day of current month
        previous_month = previous_month - timedelta(
            days=1)  # backs up a single day
        previous_month = date(year=previous_month.year,
                                       month=previous_month.month,
                                       day=1)  # find first day of previous month

        last_day = calendar.monthrange(d.year, d.month)
        next_month = date(year=d.year, month=d.month, day=last_day[
            1])  # find last day of current month
        next_month = next_month + timedelta(
            days=1)  # forward a single day
        next_month = date(year=next_month.year, month=next_month.month,
                                   day=1)  # find first day of next month

        context['previous_month'] = reverse(
            'schedule:schedule') + '?date__gte=' + str(
            previous_month)
        context['next_month'] = reverse(
            'schedule:schedule') + '?date__gte=' + str(next_month)

        day = d.weekday()
        if day != 6:
            sunday = d - timedelta(days=day + 1)
        else:
            sunday = d
        schedule = ''
        st = ScheduleTable()
        while sunday < next_month:
            schedule += "<div>"
            schedule += st.format_week(sunday)
            schedule += "</div>"
            sunday = sunday + timedelta(days=7)

        schedule = schedule.replace('<td',
                                    '<td  width="150"')
        context['schedule'] = mark_safe(schedule)
        return context


def create_schedule(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = forms.CreateScheduleForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            start_date = form.cleaned_data.get('start')
            end_date = form.cleaned_data.get('end')
            week_delta = timedelta(days=7)
            sunday = start_date
            while sunday < end_date:
                tasks.schedule_week(sunday)
                sunday = sunday + week_delta
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('schedule:calendar-index'))

    # if a GET (or any other method) we'll create a blank form
    else:
        start = Shift.last() + timedelta(days=1)
        end = start + timedelta(days=13)
        form = forms.CreateScheduleForm(initial={'start': start, 'end': end})

    return render(request, 'schedule/create-schedule.html', {'form': form})


def create_ssw(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = forms.CreateSSWForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            start_date = form.cleaned_data.get('start')
            end_date = form.cleaned_data.get('end')
            day_delta = timedelta(days=1)
            day = start_date
            while day <= end_date:
                SSW.create(day)
                day = day + day_delta
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('schedule:calendar-index'))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = forms.CreateSSWForm()

    return render(request, 'schedule/ssw-create.html', {'form': form})


def create_leave(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = forms.CreateLeaveForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            employee = form.cleaned_data.get('employee')
            start_date = form.cleaned_data.get('start')
            end_date = form.cleaned_data.get('end')
            day_delta = timedelta(days=1)
            day = start_date
            while day <= end_date:
                Leave.create(employee, day)
                day = day + day_delta
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('schedule:calendar-index'))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = forms.CreateLeaveForm()

    return render(request, 'schedule/leave-create.html', {'form': form})


def google_sync(request):
    if request.method == 'POST':
        start = request.POST.get('start', None)
        end = request.POST.get('end', None)
        if not start or not end:
            # create a form instance and populate it with data from the request:
            form = forms.GoogleSyncForm(request.POST)
            # check whether it's valid:
            if form.is_valid():
                start = form.cleaned_data.get('start')
                end = form.cleaned_data.get('end')
                tasks.sync_google_calendars(start, end)
        else:
            # perform sync
            tasks.sync_google_calendars(start, end)
            data = {
                'status': 'success',
                'start': start,
                'end': end
            }
            return JsonResponse(data)
    else:
        form = forms.GoogleSyncForm()

        return render(request, 'schedule/google-sync.html', {'form': form})


def last_scheduled_day(request):
    day = Shift.last()
    return HttpResponse(day, content_type="text/plain")


class CreateShiftView(CreateView):
    model = Shift
    fields = '__all__'


class EditShiftView(UpdateView):
    model = Shift
    fields = '__all__'


class DeleteShiftView(DeleteView):
    model = Shift
    success_url = '/'
