from . import models
import calendar
from employee.models import Employee
from schedule.models import Leave, SSW
from datetime import timedelta
from datetime import datetime
from random import seed
from random import randint
from django.db.models import Q


def sunday_list(sunday):
    order = list()
    employee_list = Employee.employee_list()
    employee_count = len(employee_list)
    delta = timedelta(days=7)
    day = sunday - delta
    while len(order) < employee_count:
        qs = models.Shift.objects.filter(date=day)
        if qs.count() == 0:
            break
        for s in qs:
            order.insert(0, s.employee)
        day = day - delta
    if len(order) < employee_count:
        if len(order) == 0:
            order = employee_list
        else:
            for emp in employee_list:
                if emp not in order:
                    order.insert(0, emp)
    return order


def schedule_sunday(sunday):
    employee_order = sunday_list(sunday)
    sunday_count = models.Shift.objects.filter(date=sunday).count()
    index = 0
    while sunday_count < 2:
        emp = employee_order[index]
        if not Leave.objects.filter(Q(date=sunday), Q(employee=emp)).exists():
            models.Shift.sunday(sunday, emp)
            sunday_count += 1
        index += 1


def schedule_sm_week(sunday, ssws):
    seed(datetime.now().microsecond)
    sm = Employee.store_manager()

    year, week, weekday = sunday.isocalendar()
    delta_day = timedelta(days=1)
    monday = sunday + delta_day
    tuesday = monday + delta_day
    wednesday = tuesday + delta_day
    thursday = wednesday + delta_day
    friday = thursday + delta_day
    saturday = friday + delta_day

    leaves = Leave.objects.filter(
        Q(employee=sm),
        Q(date__gte=sunday),
        Q(date__lte=saturday)
    )
    l_sun = leaves.filter(date=monday).exists()
    l_mon = leaves.filter(date=monday).exists()
    l_tues = leaves.filter(date=tuesday).exists()
    l_wed = leaves.filter(date=wednesday).exists()
    l_thur = leaves.filter(date=thursday).exists()
    l_fri = leaves.filter(date=friday).exists()
    l_sat = leaves.filter(date=saturday).exists()

    # monday
    if not l_mon:
        mon_shift = models.Shift.open(monday, sm)
    # tuesday
    if not l_tues:
        tues_shift = models.Shift.close(tuesday, sm)
    # wednesday
    if not l_wed:
        wed_shift = models.Shift.close(wednesday, sm)
    # thursday
    if not l_thur:
        thur_shift = models.Shift.mid(thursday, sm)
    #friday
    if not l_fri:
        fri_shift = models.Shift.open(friday, sm)
    if ssws.exists():
        if ssws.filter(date=friday).exists():
            if randint(0, 100) % 2 == 0:
                if tues_shift:
                    tues_shift.delete()
                    tues_shift = None
            else:
                if wed_shift:
                    wed_shift.delete()
                    wed_shift = None
            if thur_shift:
                thur_shift.delete()
                thur_shift = None
            if fri_shift:
                fri_shift.delete()
                fri_shift = None
            if not l_thur:
                thur_shift = models.Shift.close(thursday, sm)
            if not l_fri:
                fri_shift = models.Shift.mid(friday, sm)
            if not l_sat:
                sat_shift = models.Shift.open(saturday, sm)
        else:
            # work every other saturday
            if not l_sat:
                if week % 2 == 0:
                    if week % 4 == 0:
                        if thur_shift:
                            thur_shift.delete()
                            thur_shift = None
                        sat_shift = models.Shift.mid(saturday, sm)
                    else:
                        fri_shift.delete()
                        fri_shift = None
                        sat_shift = models.Shift.open(saturday, sm)
        if ssws.filter(date=sunday).exists():
            if not l_sun:
                if randint(0, 100) % 2 == 0:
                    if tues_shift:
                        tues_shift.delete()
                else:
                    if wed_shift:
                        wed_shift.delete()
                sun_shift = models.Shift.sunday(sunday, sm)


def schedule_asm_week(sunday, ssws):
    asm = Employee.asm()
    year, week, weekday = sunday.isocalendar()
    delta_day = timedelta(days=1)
    monday = sunday + delta_day
    tuesday = monday + delta_day
    wednesday = tuesday + delta_day
    thursday = wednesday + delta_day
    friday = thursday + delta_day
    saturday = friday + delta_day
    works_sunday = models.Shift.objects.filter(date=sunday,
                                               employee=asm).exists()

    leaves = Leave.objects.filter(
        Q(employee=asm),
        Q(date__gte=sunday),
        Q(date__lte=saturday)
    )
    l_sun = leaves.filter(date=monday).exists()
    l_mon = leaves.filter(date=monday).exists()
    l_tues = leaves.filter(date=tuesday).exists()
    l_wed = leaves.filter(date=wednesday).exists()
    l_thur = leaves.filter(date=thursday).exists()
    l_fri = leaves.filter(date=friday).exists()
    l_sat = leaves.filter(date=saturday).exists()

    # monday
    if not l_mon:
        mon_shift = models.Shift.mid(monday, asm)
    # tuesday
    if not l_tues:
        tues_shift = models.Shift.open(tuesday, asm)
    # wednesday
    if not l_wed:
        wed_shift = models.Shift.open(wednesday, asm)
    # thursday
    if not l_thur:
        thur_shift = models.Shift.close(thursday, asm)
    # friday
    if not l_fri:
        fri_shift = models.Shift.close(friday, asm)

    if ssws.exists():
        if ssws.filter(date=friday).exists():
            tuesday_count = models.Shift.objects.filter(date=tuesday).count()
            if tuesday_count == 2 and not l_tues:
                tues_shift.delete()
                tues_shift = None
            else:
                if wed_shift:
                    wed_shift.delete()
                    wed_shift = None
            if not l_fri:
                if fri_shift:
                    fri_shift.delete()
                    fri_shift = None
                fri_shift = models.Shift.open(friday, asm)
            if not l_sat:
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
        if sat_count == 0 and not l_sat:
            if randint(0, 100) % 2 == 0 and tues_shift:
                tues_shift.delete()
                tues_shift = None
            else:
                if wed_shift:
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

    if opens < 2 and scheduled_shifts['open'] == 0:
        models.Shift.open(day, rep)
        opens += 1
    elif closes < 2 and scheduled_shifts['close'] == 0:
        models.Shift.close(day, rep)
        closes += 1
    elif mids < 1 and scheduled_shifts['mid'] == 0:
        models.Shift.mid(day, rep)
        mids += 1
    elif force:
        s_open = scheduled_shifts['open']
        s_close = scheduled_shifts['close']
        s_mid = scheduled_shifts['mid']
        if s_open <= s_close and s_open < s_mid:
            models.Shift.open(day, rep)
            opens += 1
        elif s_close <= s_open and s_close < s_mid:
            models.Shift.close(day, rep)
            closes += 1
        else:
            models.Shift.early_mid(day, rep)
            mids += 1
    return opens, closes, mids


def get_lightest_day(week_dist, sunday, shift='total'):
    # Priority - Friday, Monday, Saturday, Thursday, Wednesday, Tuesday
    day = 'friday'
    d_days = 5
    if week_dist['monday'][shift] < week_dist[day][shift]:
        day = 'monday'
        d_days = 1
    if week_dist['saturday'][shift] < week_dist[day][shift]:
        day = 'saturday'
        d_days = 6
    if week_dist['thursday'][shift] < week_dist[day][shift]:
        day = 'thursday'
        d_days = 4
    if week_dist['wednesday'][shift] < week_dist[day][shift]:
        day = 'wednesday'
        d_days = 3
    if week_dist['tuesday'][shift] < week_dist[day][shift]:
        day = 'tuesday'
        d_days = 2
    return sunday + timedelta(days=d_days)


def schedule_rep_week(rep, sunday, ssws):
    year, week, weekday = sunday.isocalendar()
    delta_day = timedelta(days=1)
    monday = sunday + delta_day
    tuesday = monday + delta_day
    wednesday = tuesday + delta_day
    thursday = wednesday + delta_day
    friday = thursday + delta_day
    saturday = friday + delta_day
    works_sunday = models.Shift.objects.filter(date=sunday,
                                               employee=rep).exists()
    leaves = Leave.objects.filter(
        Q(employee=rep),
        Q(date__gte=sunday),
        Q(date__lte=saturday)
    )
    l_sun = leaves.filter(date=monday).exists()
    l_mon = leaves.filter(date=monday).exists()
    l_tues = leaves.filter(date=tuesday).exists()
    l_wed = leaves.filter(date=wednesday).exists()
    l_thur = leaves.filter(date=thursday).exists()
    l_fri = leaves.filter(date=friday).exists()
    l_sat = leaves.filter(date=saturday).exists()
    l_count = 0
    if l_sun:
        l_count += 1
    if l_mon:
        l_count += 1
    if l_tues:
        l_count += 1
    if l_wed:
        l_count += 1
    if l_thur:
        l_count += 1
    if l_fri:
        l_count += 1
    if l_sat:
        l_count += 1
    if l_count == 7:
        return

    opens = 0
    closes = 0
    mids = 0
    target_opens = 2
    target_mids = 1
    target_closes = 2
    if l_count == 6:
        target_closes = 1
        target_opens = 0
        target_opens = 0
    elif l_count == 5:
        target_opens = 1
        target_mids = 0
        target_closes = 1
    elif l_count == 4:
        target_opens = 1
        target_mids = 1
        target_closes = 1
    elif l_count == 3:
        target_opens = 1
        target_mids = 1
        target_closes = 2

    if works_sunday:
        closes += 1
    if ssws.exists():
        if ssws.filter(date=friday).exists():
            if not l_thur:
                opens, closes, mids = add_shift(
                    rep, thursday, opens, closes, mids, True
                )
            if not l_fri:
                opens, closes, mids = add_shift(
                    rep, friday, opens, closes, mids, True
                )
            if not l_sat:
                opens, closes, mids = add_shift(
                    rep, saturday, opens, closes, mids, True
                )
    else:
        if not l_thur:
            opens, closes, mids = add_shift(
                rep, thursday, opens, closes, mids
            )
        if not l_fri:
            opens, closes, mids = add_shift(
                rep, friday, opens, closes, mids
            )
        if not l_sat:
            opens, closes, mids = add_shift(
                rep, saturday, opens, closes, mids
            )
    if not l_mon:
        opens, closes, mids = add_shift(
            rep, monday, opens, closes, mids
        )
    if not l_tues:
        opens, closes, mids = add_shift(
            rep, tuesday, opens, closes, mids
        )
    if not l_wed:
        opens, closes, mids = add_shift(
            rep, wednesday, opens, closes, mids
        )
    while opens < target_opens or mids < target_mids or closes < target_closes:
        schedule_dist = models.Shift.week_shift_distribution(sunday, saturday)
        if opens < target_opens:
            day = get_lightest_day(schedule_dist, sunday, 'total')
            models.Shift.open(day, rep)
            opens += 1
        if mids < target_mids:
            day = get_lightest_day(schedule_dist, sunday, 'total')
            models.Shift.early_mid(day, rep)
            mids += 1
        if closes < target_closes:
            day = get_lightest_day(schedule_dist, sunday, 'total')
            models.Shift.close(day, rep)
            closes += 1


def schedule_week(sunday):
    saturday = sunday + timedelta(days=6)
    ssws = models.SSW.objects.filter(date__gte=sunday).filter(
        date__lte=saturday)
    schedule_sm_week(sunday, ssws)
    schedule_sunday(sunday)
    schedule_asm_week(sunday, ssws)
    reps = Employee.reps()
    for rep in reps:
        schedule_rep_week(rep, sunday, ssws)
