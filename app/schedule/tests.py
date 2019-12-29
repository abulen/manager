from django.test import TestCase
from django.contrib.auth.models import User
from employee.models import Employee, Position
from . import models
from . import tasks
import datetime


class ShiftTestCase(TestCase):

    def setUp(self):
        self.sr = Employee.objects.create_employee(
            "rep",
            None,
            None,
            Position.sales_rep()
        )

    def test_open(self):
        date = datetime.date.today()
        obj = models.Shift.open(date, self.sr)
        self.assertEqual(obj.name, "open")
        self.assertEqual(obj.date, date)
        self.assertEqual(obj.start, datetime.time(9, 0, 0))
        self.assertEqual(obj.end, datetime.time(17, 30, 0))
        self.assertEqual(obj.employee, self.sr)

    def test_close(self):
        date = datetime.date.today()
        obj = models.Shift.close(date, self.sr)
        self.assertEqual(obj.name, "close")
        self.assertEqual(obj.date, date)
        self.assertEqual(obj.start, datetime.time(12, 0, 0))
        self.assertEqual(obj.end, datetime.time(20, 0, 0))
        self.assertEqual(obj.employee, self.sr)

    def test_mid(self):
        date = datetime.date.today()
        obj = models.Shift.mid(date, self.sr)
        self.assertEqual(obj.name, "mid")
        self.assertEqual(obj.date, date)
        self.assertEqual(obj.start, datetime.time(11, 0, 0))
        self.assertEqual(obj.end, datetime.time(19, 0, 0))
        self.assertEqual(obj.employee, self.sr)

    def test_early_mid(self):
        date = datetime.date.today()
        obj = models.Shift.early_mid(date, self.sr)
        self.assertEqual(obj.name, "mid")
        self.assertEqual(obj.date, date)
        self.assertEqual(obj.start, datetime.time(10, 0, 0))
        self.assertEqual(obj.end, datetime.time(18, 0, 0))
        self.assertEqual(obj.employee, self.sr)

    def test_sunday(self):
        date = datetime.date.today()
        obj = models.Shift.sunday(date, self.sr)
        self.assertEqual(obj.name, "close")
        self.assertEqual(obj.date, date)
        self.assertEqual(obj.start, datetime.time(10, 0, 0))
        self.assertEqual(obj.end, datetime.time(17, 0, 0))
        self.assertEqual(obj.employee, self.sr)


class SSWTestCase(TestCase):

    def setUp(self):
        self.start = datetime.date.today()
        self.end = self.start + datetime.timedelta(days=5)
        self.ssw = models.SSW.create(self.start, self.end)

    def test_get_for(self):
        obj = models.SSW.get_for(self.start)
        self.assertEqual(obj, self.ssw)
        self.assertEqual(obj.start, self.start)
        self.assertEqual(obj.end, self.end)
        self.assertTrue(obj.falls_within(
            self.start + datetime.timedelta(days=1)
        ))
        self.assertFalse(obj.falls_within(
            self.end + datetime.timedelta(days=1)
        ))


class TaskTestCase(TestCase):

    def setUp(self):
        self.sm = Employee.objects.create_employee(
            "sm",
            None,
            None,
            Position.store_manager()
        )
        self.asm = Employee.objects.create_employee(
            "asm",
            None,
            None,
            Position.assistant_store_manager()
        )
        self.sr1 = Employee.objects.create_employee("rep1")
        self.sr2 = Employee.objects.create_employee("rep2")
        self.sr3 = Employee.objects.create_employee("rep3")

    def test_schedule_week(self):
        day = datetime.date.today()
        tasks.schedule_week(day)
        self.assertFalse(models.Shift.objects.filter(date=day).count() == 0)


