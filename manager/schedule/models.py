"""
Schedule Models
===============
"""
from django.db import models
from django.db.models import Q
from employee.models import Employee
from django.urls import reverse
from django.contrib.auth.models import User
import datetime
import calendar


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

    def get_absolute_url(self):
        url = reverse('admin:%s_%s_change' % (
        self._meta.app_label, self._meta.model_name), args=[self.id])
        return u'<a class="shift" href="%s">%s <br> %s - %s</a>' % (url,
                                                 self.employee.user.username,
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
    def open(date, employee):
        return Shift.objects.create(
            name='open',
            date=date,
            start=datetime.time(9, 0, 0),
            end=datetime.time(17, 30, 0),
            employee=employee
        )

    @staticmethod
    def mid(date, employee):
        return Shift.objects.create(
            name='mid',
            date=date,
            start=datetime.time(11, 0, 0),
            end=datetime.time(19, 0, 0),
            employee=employee
        )

    @staticmethod
    def early_mid(date, employee):
        return Shift.objects.create(
            name='mid',
            date=date,
            start=datetime.time(10, 0, 0),
            end=datetime.time(18, 0, 0),
            employee=employee
        )

    @staticmethod
    def close(date, employee):
        return Shift.objects.create(
            name='close',
            date=date,
            start=datetime.time(12, 0, 0),
            end=datetime.time(20, 0, 0),
            employee=employee
        )

    @staticmethod
    def sunday(date, employee):
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


class Leave(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='leaves'
    )
    date = models.DateField()

    def get_absolute_url(self):
        url = reverse('admin:%s_%s_change' % (
        self._meta.app_label, self._meta.model_name), args=[self.id])
        return u'<a class="leave" href="%s">leave - %s</a>' % (url,
                                                 self.employee.user.username)

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

    def get_absolute_url(self):
        url = reverse('admin:%s_%s_change' % (
        self._meta.app_label, self._meta.model_name), args=[self.id])
        return u'<a class="ssw" href="%s">SSW</a>' % (url, )
