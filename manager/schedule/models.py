"""
Schedule Models
===============
"""
from django.db import models
from django.contrib.auth.models import User
import datetime


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


class Shift(models.Model):
    name = models.CharField(max_length=30, blank=True)
    start = models.TimeField()
    end = models.TimeField()

    def __str__(self):
        return self.name

    @staticmethod
    def open():
        s, created = Shift.objects.get_or_create(
            name='open',
            defaults={'start':datetime.time(9, 0, 0),
                      'end':datetime.time(17, 30, 0)}
        )
        return s

    @staticmethod
    def mid():
        s, created = Shift.objects.get_or_create(
            name='mid',
            defaults={'start': datetime.time(11, 0, 0),
                      'end': datetime.time(19, 0, 0)}
        )
        return s

    @staticmethod
    def early_mid():
        s, created = Shift.objects.get_or_create(
            name='late_mid',
            defaults={'start': datetime.time(10, 0, 0),
                      'end': datetime.time(18, 0, 0)}
        )
        return s

    @staticmethod
    def close():
        s, created = Shift.objects.get_or_create(
            name='close',
            defaults={'start': datetime.time(12, 0, 0),
                      'end': datetime.time(20, 0, 0)}
        )
        return s

    @staticmethod
    def sunday():
        s, created = Shift.objects.get_or_create(
            name='sunday',
            defaults={'start': datetime.time(10, 0, 0),
                      'end': datetime.time(17, 0, 0)}
        )
        return s


class Day(models.Model):
    date = models.DateField()
    week_day = models.CharField(max_length=20, blank=True)
    open = models.ManyToManyField(Employee, related_name='opens')
    mid = models.ManyToManyField(Employee, related_name='mids')
    early_mid = models.ManyToManyField(Employee, related_name='early_mids')
    close = models.ManyToManyField(Employee, related_name='closes')
    sunday_shift = models.ManyToManyField(Employee, related_name='sunday_shifts')
    off = models.ManyToManyField(Employee, related_name='offs')

    def __str__(self):
        return self.week_day + str(self.date)

    @staticmethod
    def sunday(date):
        return Day.objects.create(week_day="Sunday", date=date)

    @staticmethod
    def monday(date):
        return Day.objects.create(week_day="Monday", date=date)

    @staticmethod
    def tuesday(date):
        return Day.objects.create(week_day="Tuesday", date=date)

    @staticmethod
    def wednesday(date):
        return Day.objects.create(week_day="Wednesday", date=date)

    @staticmethod
    def thursday(date):
        return Day.objects.create(week_day="Thursday", date=date)

    @staticmethod
    def friday(date):
        return Day.objects.create(week_day="Friday", date=date)

    @staticmethod
    def saturday(date):
        return Day.objects.create(week_day="Saturday", date=date)


class Week(models.Model):
    sunday = models.ForeignKey(
        Day,
        related_name='sundays',
        on_delete=models.CASCADE
    )
    monday = models.ForeignKey(
        Day,
        related_name='mondays',
        on_delete=models.CASCADE
    )
    tuesday = models.ForeignKey(
        Day,
        related_name='tuesdays',
        on_delete=models.CASCADE
    )
    wednesday = models.ForeignKey(
        Day,
        related_name='wednesdays',
        on_delete=models.CASCADE
    )
    thursday = models.ForeignKey(
        Day,
        related_name='thursdays',
        on_delete=models.CASCADE
    )
    friday = models.ForeignKey(
        Day,
        related_name='fridays',
        on_delete=models.CASCADE
    )
    saturday = models.ForeignKey(
        Day,
        related_name='saturdays',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.sunday.date) + " - " + str(self.saturday.date)

    def schedule_sunday(self):
        employee = Employee.objects.all().order_by('sunday_shifts__date')[:1].get()
        self.sunday.sunday_shift.add(employee)

    @staticmethod
    def previous_week(week):
        prev_sun_date = week.sunday.date - datetime.timedelta(days=7)
        try:
            prev_week = Week.objects.get(sunday__date=prev_sun_date)
        except Week.DoesNotExist:
            prev_week = Week.create(prev_sun_date)
            sm = Employee.store_manager()
            asm = Employee.store_manager()
            prev_week.sunday.off.add(sm)
            prev_week.sunday.off.add(asm)
            prev_week.monday.off.add(sm)
            prev_week.monday.off.add(asm)
            prev_week.tuesday.off.add(sm)
            prev_week.tuesday.off.add(asm)
            prev_week.wednesday.off.add(sm)
            prev_week.wednesday.off.add(asm)
            prev_week.thursday.off.add(sm)
            prev_week.thursday.off.add(asm)
            prev_week.friday.off.add(sm)
            prev_week.friday.off.add(asm)
            prev_week.saturday.off.add(sm)
            prev_week.saturday.off.add(asm)
            prev_week.save()
        return prev_week

    @staticmethod
    def schedule_shifts(week, prev_week):
        sm = Employee.store_manager()
        week = sm.schedule_manager_week(week, prev_week)
        asm = Employee.asm()
        week = asm.schedule_asm_week(week, prev_week)
        reps = Employee.objects.filter(
            position=Position.sales_rep()).order_by('sundays__date')
        for rep in reps:
            week = rep.schedule_rep_week(week)
        return week

    @staticmethod
    def create(start):
        week = Week.objects.create(
            sunday=Day.sunday(start),
            monday=Day.monday(start+datetime.timedelta(days=1)),
            tuesday=Day.tuesday(start+datetime.timedelta(days=2)),
            wednesday=Day.wednesday(start+datetime.timedelta(days=3)),
            thursday=Day.thursday(start+datetime.timedelta(days=4)),
            friday=Day.friday(start+datetime.timedelta(days=5)),
            saturday=Day.saturday(start+datetime.timedelta(days=6))
        )
        return week

    @staticmethod
    def create_schedule(start):
        week = Week.create(start)
        prev_week = Week.previous_week(week)
        print(prev_week)
        week = week.schedule_shifts(week, prev_week)
        week.save()
        return week

