from . import models
import calendar
from datetime import timedelta
from datetime import datetime
from random import seed
from random import randint


def sunday_list(sunday):
    order = list()
    employee_list = models.Employee.employee_list()
    employee_count = employee_list.count()
    delta = timedelta(days=7)
    day = sunday - delta
    while order.count() < employee_count:
        qs = models.Shift.filter(date=day)
        if qs.count() == 0:
            break
        for s in qs:
            order.append(s.employee)
        day = day - delta
    if order.count() < employee_count:
        if order.count() == 0:
            order = employee_list
        else:
            for emp in employee_list:
                if not order.contains(emp):
                    order.insert(0, emp)
    return order


def schedule_sunday(sunday):
    employee_order = sunday_list()
    sunday_count = models.Shift.filter(day=sunday).count()
    index = 0
    while sunday_count < 2:
        models.Shift.sunday(sunday, employee_order[index])
        sunday_count += 1
        index += 1


def schedule_sm_week(sunday, ssw=None):
    seed(datetime.now().microsecond)
    sm = models.Employee.store_manager()
    year, week, weekday = sunday.isocalendar()
    delta_day = timedelta(day=1)
    monday = sunday + delta_day
    tuesday = monday + delta_day
    wednesday = tuesday + delta_day
    thursday = wednesday + delta_day
    friday = thursday + delta_day
    saturday = friday + delta_day

    # monday
    mon_shift = models.Shift.open(monday, sm)
    # tuesday
    tues_shift = models.Shift.close(tuesday, sm)
    # wednesday
    wed_shift = models.Shift.close(wednesday, sm)
    # thursday
    thur_shift = models.Shift.mid(thursday, sm)
    #friday
    fri_shift = models.Shift.open(friday, sm)
    if ssw:
        if ssw.falls_within(friday):
            if randint() % 2 == 0:
                tues_shift.delete()
            else:
                wed_shift.delete()
            thur_shift.delete()
            thur_shift = models.Shift.close(thursday, sm)
            fri_shift = models.Shift.mid(friday, sm)
            sat_shift = models.Shift.open(saturday, sm)
        else:
            # work every other saturday
            if week % 2 == 0:
                if week % 4 == 0:
                    thur_shift.delete()
                    sat_shift = models.Shift.mid(saturday, sm)
                else:
                    fri_shift.delete()
                    sat_shift = models.Shift.open(saturday, sm)
        if ssw.falls_within(sunday):
            if randint() % 2 == 0:
                tues_shift.delete()
            else:
                wed_shift.delete()
            sun_shift = models.Shift.sunday(sunday, sm)


def schedule_asm_week(sunday, ssw=None):
    asm = models.Employee.asm()
    year, week, weekday = sunday.isocalendar()
    delta_day = timedelta(day=1)
    monday = sunday + delta_day
    tuesday = monday + delta_day
    wednesday = tuesday + delta_day
    thursday = wednesday + delta_day
    friday = thursday + delta_day
    saturday = friday + delta_day
    works_sunday = models.Shift.objects.filter(date=sunday,
                                               employee=asm).exists()

    # monday
    mon_shift = models.Shift.mid(monday, asm)
    # tuesday
    tues_shift = models.Shift.open(tuesday, asm)
    # wednesday
    wed_shift = models.Shift.open(wednesday, asm)
    # thursday
    thur_shift = models.Shift.close(thursday, asm)
    # friday
    fri_shift = models.Shift.close(friday, asm)

    if ssw:
        if ssw.falls_within(friday):
            tuesday_count = models.Shift.objects.filter(date=tuesday).count()
            if tuesday_count == 2:
                tues_shift.delete()
                tues_shift = None
            else:
                wed_shift.delete()
                wed_shift = None
            fri_shift = models.Shift.open(friday, asm)
            sat_shift = models.Shift.close(saturday, asm)
            if works_sunday:
                if tues_shift:
                    tues_shift.delete()
                    tues_shift = None
                elif wed_shift:
                    wed_shift.delete()
                    wed_shift = None
                elif mon_shift:
                    mon_shift.delete
                    mon_shift = None
    else:
        sat_count = models.Shift.objects.filter(date=saturday).count()
        if sat_count == 0:
            if randint() % 2 == 0:
                tues_shift.delete()
                tues_shift = None
            else:
                wed_shift.delete()
                wed_shift = None
            sat_shift = models.Shift.open(saturday, asm)
        if works_sunday:
            if fri_shift:
                fri_shift.delete()
                fri_shift = None
            elif thur_shift:
                thur_shift.delete()
                thur_shift = None
            elif mon_shift:
                mon_shift.delete
                mon_shift = None


def add_shift(rep, day, opens, closes, mids, force=False):
    scheduled_shifts = models.Shift.on_day(day)
    if opens < 2 and not scheduled_shifts['open']:
        models.Shift.open(day, rep)
        opens += 1
    elif closes < 2 and not scheduled_shifts['close']:
        models.Shift.close(day, rep)
        closes += 1
    elif mids < 1:
        if not scheduled_shifts['mid']:
            models.Shift.mid(day, rep)
            mids += 1
        else:
            if force:
                models.Shift.early_mid(day, rep)
                mids += 1
    return opens, closes, mids


def schedule_rep_week(rep, sunday, ssw=None):
    year, week, weekday = sunday.isocalendar()
    delta_day = timedelta(day=1)
    monday = sunday + delta_day
    tuesday = monday + delta_day
    wednesday = tuesday + delta_day
    thursday = wednesday + delta_day
    friday = thursday + delta_day
    saturday = friday + delta_day
    works_sunday = models.Shift.objects.filter(date=sunday,
                                               employee=rep).exists()

    opens = 0
    closes = 0
    mids = 0
    if ssw:
        if ssw.falls_within(friday):
            opens, closes, mids = add_shift(
                rep, thursday, opens, closes, mids, True
            )
            opens, closes, mids = add_shift(
                rep, friday, opens, closes, mids, True
            )
            opens, closes, mids = add_shift(
                rep, saturday, opens, closes, mids, True
            )
    else:
        opens, closes, mids = add_shift(
            rep, thursday, opens, closes, mids
        )
        opens, closes, mids = add_shift(
            rep, friday, opens, closes, mids
        )
        opens, closes, mids = add_shift(
            rep, saturday, opens, closes, mids
        )
    opens, closes, mids = add_shift(
        rep, monday, opens, closes, mids
    )
    opens, closes, mids = add_shift(
        rep, tuesday, opens, closes, mids
    )
    opens, closes, mids = add_shift(
        rep, wednesday, opens, closes, mids
    )


def schedule_week(sunday):
    ssw = models.SSW.get_for(sunday + timedelta(days=5))
    if not ssw.exists():
        ssw = models.SSW.get_for(sunday)
    if not ssw.exists():
        ssw = None
    schedule_sm_week(sunday)
    schedule_sunday(sunday)
    schedule_asm_week(sunday, ssw)
    reps = models.Employee.reps()
    for rep in reps:
        schedule_rep_week(rep, sunday, ssw)
