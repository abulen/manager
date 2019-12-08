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
        max_length='20',
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

    def schedule_manager_week(self, week, previous_week):
        offs = 0
        opens = 0
        mids = 0
        closes = 0
        if self in week.sunday.sunday_shift.all():
            closes += 1
        else:
            week.sunday.off.add(self)
            offs += 1
        # saturday
        worked_saturday = False
        sat_open = False
        if previous_week:
            if self in previous_week.saturday.open.all():
                worked_saturday = True
                sat_open = True
            elif self in previous_week.saturday.mid.all():
                worked_saturday = True
            if worked_saturday:
                week.saturday.off.add(self)
                offs += 1
            else:
                if sat_open:
                    week.saturday.mid.add(self)
                    mids += 1
                else:
                    week.saturday.open.add(self)
                    opens += 1
        else:
            week.saturday.open.add(self)
            opens += 1
        # monday
        week.monday.open.add(self)
        # friday
        work_friday = False
        if self in previous_week.friday.off.all():
            work_friday = True
        if offs < 2:
            work_friday = True
        if work_friday:
            if opens < 2:
                week.friday.open.add(self)
                opens += 1
            elif mids == 0:
                week.friday.mid.add(self)
                mids += 1
            if closes < 2:
                week.friday.close.add(self)
                closes += 1
            else:
                week.friday.off.add(self)
        # tuesday
        work_tuesday = False
        if self in previous_week.tuesday.off.all():
            work_tuesday = True
        if offs < 2:
            work_tuesday = True
        if work_tuesday:
            if closes < 2:
                week.tuesday.close.add(self)
                closes += 1
            elif mids == 0:
                week.tuesday.mid.add(self)
                mids += 1
            elif opens < 2:
                week.tuesday.open.add(self)
                opens += 1
        # wednesday
        work_wednesday = False
        if self in previous_week.wednesday.off.all():
            work_wednesday = True
        if offs < 2:
            work_wednesday = True
        if work_wednesday:
            if opens < 2:
                week.wednesday.open.add(self)
                opens += 1
            elif mids == 0:
                week.wednesday.mid.add(self)
                mids += 1
            if closes < 2:
                week.wednesday.close.add(self)
                closes += 1
            else:
                week.wednesday.off.add(self)
        # thursday
        work_thursday = False
        if self in previous_week.thursday.off.all():
            work_thursday = True
        if offs < 2:
            work_thursday = True
        if work_thursday:
            if closes < 2:
                week.thursday.close.add(self)
                closes += 1
            elif mids == 0:
                week.thursday.mid.add(self)
                mids += 1
            elif opens < 2:
                week.thursday.open.add(self)
                opens += 1
        week.save()
        return week

    def schedule_asm_week(self, week, previous_week):
        sm = Employee.store_manager()
        offs = 0
        opens = 0
        mids = 0
        closes = 0
        prev_offs = offs
        if self in week.sunday.sunday_shift.all():
            closes += 1
            offs += 1
        sunday = prev_offs == offs
        # saturday
        prev_offs = offs
        if sm in week.saturday.off.all():
            worked_saturday = False
            sat_open = False
            if previous_week:
                if self in previous_week.saturday.open.all():
                    worked_saturday = True
                    sat_open = True
                elif self in previous_week.saturday.mid.all():
                    worked_saturday = True
                if worked_saturday:
                    week.saturday.off.add(self)
                    offs += 1
                else:
                    if sat_open:
                        week.saturday.mid.add(self)
                        mids += 1
                    else:
                        week.saturday.open.add(self)
                        opens += 1
            else:
                week.saturday.open.add(self)
                opens += 1
        else:
            week.saturday.off.add(self)
            offs += 1
        saturday = prev_offs == offs
        # work sm off days
        prev_offs = offs
        if sm in week.monday.off.all():
            week.monday, opens, mids, closes, offs = self.schedule_day(
                week.monday, opens, mids, closes, offs
            )
        monday = prev_offs == offs
        prev_offs = offs
        if sm in week.tuesday.off.all():
            week.tuesday, opens, mids, closes, offs = self.schedule_day(
                week.tuesday, opens, mids, closes, offs
            )
        tuesday = prev_offs == offs
        prev_offs = offs
        if sm in week.wednesday.off.all():
            week.wednesday, opens, mids, closes, offs = self.schedule_day(
                week.wednesday, opens, mids, closes, offs
            )
        wednesday = prev_offs == offs
        prev_offs = offs
        if sm in week.thursday.off.all():
            week.thursday, opens, mids, closes, offs = self.schedule_day(
                week.thursday, opens, mids, closes, offs
            )
        thursday = prev_offs == offs
        prev_offs = offs
        if sm in week.friday.off.all():
            week.friday, opens, mids, closes, offs = self.schedule_day(
                week.friday, opens, mids, closes, offs
            )
        friday = prev_offs == offs
        # fill the rest of the days
        if not monday and offs < 2:
            week.monday.off.add(self)
        else:
            week.monday, opens, mids, closes, offs = self.schedule_day(
                week.monday, opens, mids, closes, offs
            )
        if not tuesday and offs < 2:
            week.tuesday.off.add(self)
        else:
            week.tuesday, opens, mids, closes, offs = self.schedule_day(
                week.tuesday, opens, mids, closes, offs
            )
        if not wednesday and offs < 2:
            week.wednesday.off.add(self)
        else:
            week.wednesday, opens, mids, closes, offs = self.schedule_day(
                week.wednesday, opens, mids, closes, offs
            )
        if not thursday and offs < 2:
            week.thursday.off.add(self)
        else:
            week.thursday, opens, mids, closes, offs = self.schedule_day(
                week.thursday, opens, mids, closes, offs
            )
        if not friday and offs < 2:
            week.friday.off.add(self)
        else:
            week.friday, opens, mids, closes, offs = self.schedule_day(
                week.friday, opens, mids, closes, offs
            )
        if not sunday and offs < 2:
            week.sunday.sunday_shift.add(self)
        week.save()
        return week

    def schedule_day(self, day, opens, mids, closes, offs):
        if opens < 2:
            if day.open.all().count() == 0:
                day.open.add(self)
                opens += 1
        elif mids < 1:
            if day.mid.all().count() == 0:
                day.mid.add(self)
                mids += 1
        elif closes < 2:
            if day.close.all().count() == 0:
                day.close.add(self)
                closes += 1
        elif offs < 2:
            day.off.add(self)
            offs += 1
        else:
            day.early_mid.add(self)
        day.save()
        return day, opens, mids, closes, offs

    def schedule_rep_week(self, week):
        offs = 0
        opens = 0
        mids = 0
        closes = 0
        prev = closes
        if self in week.sunday.sunday_shift.all():
            closes += 1
        sunday = closes == prev
        #saturday
        week.saturday, opens, mids, closes, offs = self.schedule_day(
            week.saturday, opens, mids, closes, offs
        )
        # friday
        week.friday, opens, mids, closes, offs = self.schedule_day(
            week.friday, opens, mids, closes, offs
        )
        # thursday
        week.thursday, opens, mids, closes, offs = self.schedule_day(
            week.thursday, opens, mids, closes, offs
        )
        # wednesday
        week.wednesday, opens, mids, closes, offs = self.schedule_day(
            week.wednesday, opens, mids, closes, offs
        )
        # tuesday
        week.tuesday, opens, mids, closes, offs = self.schedule_day(
            week.tuesday, opens, mids, closes, offs
        )
        # monday
        week.monday, opens, mids, closes, offs = self.schedule_day(
            week.monday, opens, mids, closes, offs
        )
        # sunday
        week.sunday, opens, mids, closes, offs = self.schedule_day(
            week.sunday, opens, mids, closes, offs
        )
        week.save()
        return week

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
        employees = list()
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
        ret = 'close ' + str(self.date)
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
        return SSW.objects.get(
            Q(start__lte=date),
            Q(end__qte=date)
        )

    def falls_within(self, date):
        if date < self.start:
            return False
        if date > self.end:
            return False
        return True
