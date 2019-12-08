"""
Schedule Models
===============
"""
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
import datetime
import calendar


class Position(models.Model):
    name = models.CharField(max_length=50, blank=True)
    manager = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.name

    @staticmethod
    def store_manager():
        obj, created = Position.objects.get_or_create(
            name='Store Manager',
            defaults={'manager': True}
        )
        return obj

    @staticmethod
    def assistant_store_manager():
        obj, created = Position.objects.get_or_create(
            name='Assistant Store Manager',
            defaults={'manager': True}
        )
        return obj

    @staticmethod
    def sales_rep():
        obj, created = Position.objects.get_or_create(
            name='Sales Representative',
            defaults={'manager': False}
        )
        return obj


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
    )
    status_options = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    status = models.CharField(
        max_length=20,
        choices=status_options,
        default='active'
    )

    def __str__(self):
        return self.user.username

    @staticmethod
    def store_manager():
        return Employee.objects.get(position=Position.store_manager())

    @staticmethod
    def asm():
        return Employee.objects.get(position=Position.assistant_store_manager())

    @staticmethod
    def employee_list():
        employees = list()
        sm = Position.store_manager()
        qs = Employee.objects.filter(status='active')
        for emp in qs:
            if emp.position != sm:
                employees.append(emp)
        return employees

    @staticmethod
    def reps():
        rep = Position.sales_rep()
        return Employee.objects.filter(status='active', position=rep)


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
        ret['open'] = False
        ret['mid'] = False
        ret['close'] = False
        shifts = Shift.objects.filter(date=day)
        if shifts.exists():
            for shift in shifts:
                if shift.is_open():
                    ret['open'] = True
                elif shift.is_close():
                    ret['close'] = True
                elif shift.is_mid():
                    ret['mid'] = True
        return ret

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
            start=datetime.time(10, 0, 0),
            end=datetime.time(17, 0, 0),
            employee=employee
        )


class Leave(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='leaves'
    )
    start = models.DateField()
    end = models.DateField()


class SSW(models.Model):
    start = models.DateField()
    end = models.DateField()

    @staticmethod
    def create(start, end):
        return SSW.objects.create(
            start=start,
            end=end
        )

    @staticmethod
    def get_for(date):
        try:
            qs = SSW.objects.get(
                Q(start__lte=date),
                Q(end__gte=date)
            )
            return qs
        except SSW.DoesNotExist:
            return None

    def falls_within(self, date):
        if date < self.start:
            return False
        if date > self.end:
            return False
        return True
