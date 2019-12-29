"""
Schedule Models
===============
"""
from django.db import models
from django.db.models import Count
from django.db.models import Q
from employee.models import Employee
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
import datetime
import calendar
from pytz import reference

from django.conf import settings
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class Shift(models.Model):
    name = models.CharField(max_length=30, blank=True)
    date = models.DateField()
    start = models.TimeField()
    end = models.TimeField()
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='shifts'
    )

    def get_calendar_url(self):
        url = reverse('admin:%s_%s_change' % (
        self._meta.app_label, self._meta.model_name), args=[self.id])
        return u'<a class="shift" href="%s">%s %s<br> %s - %s</a>' % (
            url,
            self.employee.user.first_name,
            self.employee.user.last_name,
            self.start.strftime("%I:%M"),
            self.end.strftime("%I:%M")
        )

    def __str__(self):
        ret = self.name + ' ' + str(self.date)
        if self.employee:
            ret = ret + " - " + self.employee.user.username
        return ret

    def is_open(self):
        return self.name == 'open'

    def is_mid(self):
        return self.name == 'mid'

    def is_close(self):
        return self.name == 'close'

    @staticmethod
    def on_day(day):
        ret = dict()
        ret['open'] = 0
        ret['mid'] = 0
        ret['close'] = 0
        ret['total'] = 0
        shifts = Shift.objects.filter(date=day)
        if shifts.exists():
            for shift in shifts:
                if shift.is_open():
                    ret['open'] += 1
                elif shift.is_close():
                    ret['close'] += 1
                elif shift.is_mid():
                    ret['mid'] += 1
                ret['total'] += 1
        return ret

    @staticmethod
    def week_shift_distribution(sunday, saturday):
        day_delta = datetime.timedelta(days=1)
        monday = sunday + day_delta
        tuesday = monday + day_delta
        wednesday = tuesday + day_delta
        thursday = wednesday + day_delta
        friday = thursday + day_delta
        shifts = dict()
        shifts["sunday"] = Shift.on_day(sunday)
        shifts["monday"] = Shift.on_day(monday)
        shifts["tuesday"] = Shift.on_day(tuesday)
        shifts["wednesday"] = Shift.on_day(wednesday)
        shifts["thursday"] = Shift.on_day(thursday)
        shifts["friday"] = Shift.on_day(friday)
        shifts["saturday"] = Shift.on_day(saturday)
        return shifts

    @staticmethod
    def week_order(sunday):
        saturday = sunday + datetime.timedelta(days=6)
        qs = Shift.objects.filter(
            Q(date__gte=sunday),
            Q(date__lte=saturday)
        )
        day_shifts = dict()
        day_shifts["monday"] = qs.filter(
            date=sunday+datetime.timedelta(days=1)).count()
        day_shifts["tuesday"] = qs.filter(
            date=sunday+datetime.timedelta(days=2)).count()
        day_shifts["wednesday"] = qs.filter(
            date=sunday+datetime.timedelta(days=3)).count()
        day_shifts["thursday"] = qs.filter(
            date=sunday+datetime.timedelta(days=4)).count()
        day_shifts["friday"] = qs.filter(
            date=sunday+datetime.timedelta(days=5)).count()
        day_shifts["saturday"] = qs.filter(
            date=sunday+datetime.timedelta(days=6)).count()
        order_kv = sorted(day_shifts.items(),
                          key=lambda kv: (kv[1], kv[0]))
        order = list()
        for key, value in order_kv:
            order.append(key)
        return order

    @staticmethod
    def open(date, employee):
        if Shift.is_working(employee, date):
            return None
        else:
            return Shift.objects.create(
                name='open',
                date=date,
                start=datetime.time(9, 0, 0),
                end=datetime.time(17, 30, 0),
                employee=employee
            )

    @staticmethod
    def mid(date, employee):
        if Shift.is_working(employee, date):
            return None
        else:
            return Shift.objects.create(
                name='mid',
                date=date,
                start=datetime.time(11, 0, 0),
                end=datetime.time(19, 0, 0),
                employee=employee
            )

    @staticmethod
    def early_mid(date, employee):
        if Shift.is_working(employee, date):
            return None
        else:
            return Shift.objects.create(
                name='mid',
                date=date,
                start=datetime.time(10, 0, 0),
                end=datetime.time(18, 0, 0),
                employee=employee
            )

    @staticmethod
    def close(date, employee):
        if Shift.is_working(employee, date):
            return None
        else:
            return Shift.objects.create(
                name='close',
                date=date,
                start=datetime.time(12, 0, 0),
                end=datetime.time(20, 0, 0),
                employee=employee
            )

    @staticmethod
    def sunday(date, employee):
        if Shift.is_working(employee, date):
            return None
        else:
            return Shift.objects.create(
                name='close',
                date=date,
                start=datetime.time(11, 0, 0),
                end=datetime.time(17, 0, 0),
                employee=employee
            )

    @staticmethod
    def last():
        qs = Shift.objects.all().order_by('-date')
        if qs.exists():
            day = qs[0].date
        else:
            day = datetime.date.today() - datetime.timedelta(days=1)
        return day

    @staticmethod
    def is_working(employee, date):
        return Shift.objects.filter(employee=employee, date=date).exists()


class Leave(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='leaves'
    )
    date = models.DateField()

    def get_calendar_url(self):
        url = reverse('admin:%s_%s_change' % (
        self._meta.app_label, self._meta.model_name), args=[self.id])
        return u'<a class="leave" href="%s">leave - %s %s</a>' % (
            url,
            self.employee.user.first_name,
            self.employee.user.last_name
        )

    @staticmethod
    def create(emp, day):
        return Leave.objects.get_or_create(
            employee=emp,
            date=day
        )


class SSW(models.Model):
    date = models.DateField()

    @staticmethod
    def create(day):
        return SSW.objects.get_or_create(
            date=day
        )

    @staticmethod
    def get_for(date):
        try:
            qs = SSW.objects.get(
                Q(date=date)
            )
            return qs
        except SSW.DoesNotExist:
            return None

    def get_calendar_url(self):
        url = reverse('admin:%s_%s_change' % (
        self._meta.app_label, self._meta.model_name), args=[self.id])
        return u'<a class="ssw" href="%s">SSW</a>' % (url, )


class GoogleCalendar(models.Model):
    name = models.CharField(max_length=50, blank=True)
    calendar_id = models.CharField(max_length=50, blank=True)
    credentials = models.FileField(upload_to=settings.CREDENTIALS_DIR,
                                   max_length=100)
    token = models.FileField(upload_to=settings.CREDENTIALS_DIR,
                             max_length=100)

    @staticmethod
    def create(name, cid):
        obj = GoogleCalendar.objects.create(
            name=name,
            calendar_id=cid
        )
        obj.credentials.save(name+".json", ContentFile(""))
        obj.token.save(name+".pickle", ContentFile(""))
        return obj.save()

    @staticmethod
    def local_tz():
        return reference.LocalTimezone().tzname(
            datetime.datetime.today())

    def get_credentials(self):
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials,
            scopes=settings.GOOGLE_CALENDAR_SCOPES)
        credentials = flow.run_console()
        return credentials

    def get_service(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self.token):
            with open(self.token, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials, settings.GOOGLE_CALENDAR_SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.token, 'wb') as token:
                pickle.dump(creds, token)

        service = build('calendar', 'v3', credentials=creds)
        return service

    def create_event(self, date, summary, start_time, end_time, description):
        start = datetime.datetime.combine(date, start_time)
        end = datetime.datetime.combine(date, end_time)
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': self.local_tz(),
            },
            'end': {
                'dateTime': end.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': self.local_tz(),
            },
        }
        service = self.get_service()
        return service.events().insert(calendarId=self.calendar_id, body=event,
                                       sendNotifications=False).execute()

    def create_day_event(self, date, summary, description):
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': date.strftime("%Y-%m-%d"),
                'timeZone': self.local_tz(),
            },
            'end': {
                'dateTime': date.strftime("%Y-%m-%d"),
                'timeZone': self.local_tz(),
            },
        }
        service = self.get_service()
        return service.events().insert(calendarId=self.calendar_id, body=event,
                                       sendNotifications=False).execute()

    def delete_event(self, event_id):
        service = self.get_service()
        return service.events().delete(calendarId=self.calendar_id,
                                       eventId=event_id).execute()

    def get_events(self, before_date, after_date):
        service = self.get_service()
        events_result = service.events().list(
            calendarId=self.calendar_id,
            timeMin=after_date.strftime("%Y-%m-%d"),
            timeMax=before_date.strftime("%Y-%m-%d"),
            singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])
        return events

    def create_shift(self, shift):
        emp = shift.employee.user.first_name + " " + \
              shift.employee.user.last_name
        return self.create_event(shift.date, emp,
                                 shift.start, shift.end,
                                 emp)

    def create_ssw(self, ssw):
        return self.create_day_event(ssw.date, "SSW", "SSW")

    def create_leave(self, leave):
        summary = leave.employee.user.first_name + " " + \
                  leave.employee.user.last_name + " Leave"
        return self.create_day_event(leave.date, summary, summary)

    def sync(self, start_date, end_date):
        # delete existing events
        day_delta = datetime.timedelta(days=1)
        events = self.get_events(start_date - day_delta, end_date + day_delta)
        for event in events:
            self.delete_event(event['id'])
        # create SSWs
        ssws = SSW.objects.filter(
            Q(date__gte=start_date),
            Q(date__lte=end_date)
        )
        for ssw in ssws:
            self.create_ssw(ssw)
        # create leave
        leaves = Leave.objects.filter(
            Q(date__gte=start_date),
            Q(date__lte=end_date)
        )
        for leave in leaves:
            self.create_leave(leave)
        # create shifts
        shifts = Shift.objects.filter(
            Q(date__gte=start_date),
            Q(date__lte=end_date)
        )
        for shift in shifts:
            self.create_shift(shift)


