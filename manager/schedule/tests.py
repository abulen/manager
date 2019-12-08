from django.test import TestCase
from django.contrib.auth.models import User
from . import models
from . import tasks
import datetime


class PositionTestCase(TestCase):

    def test_sales_rep(self):
        obj = models.Position.sales_rep()
        self.assertEqual(obj.manager, False)
        self.assertEqual(obj.name, "Sales Representative")

    def test_store_manager(self):
        obj = models.Position.store_manager()
        self.assertEqual(obj.manager, True)
        self.assertEqual(obj.name, "Store Manager")

    def test_assistant_store_manager(self):
        obj = models.Position.assistant_store_manager()
        self.assertEqual(obj.manager, True)
        self.assertEqual(obj.name, "Assistant Store Manager")


class EmployeeTestCase(TestCase):

    def setUp(self):
        user_sm = User.objects.create_user('sm')
        user_asm = User.objects.create_user("asm")
        user_sr = User.objects.create_user("rep")
        self.sm = models.Employee.objects.create(
            user=user_sm,
            position=models.Position.store_manager()
        )
        self.asm = models.Employee.objects.create(
            user=user_asm,
            position=models.Position.assistant_store_manager()
        )
        self.sr = models.Employee.objects.create(
            user=user_sr,
            position=models.Position.sales_rep()
        )

    def test_sm(self):
        obj = models.Employee.store_manager()
        self.assertEqual(obj, self.sm)

    def test_asm(self):
        obj = models.Employee.asm()
        self.assertEqual(obj, self.asm)

    def test_sr(self):
        obj = models.Employee.reps()
        self.assertEqual(obj.count(), 1)
        self.assertEqual(obj.first(), self.sr)


class ShiftTestCase(TestCase):

    def setUp(self):
        user_sr = User.objects.create_user("rep")
        self.sr = models.Employee.objects.create(
            user=user_sr,
            position=models.Position.sales_rep()
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
        user_sm = User.objects.create_user('sm')
        user_asm = User.objects.create_user("asm")
        user_sr1 = User.objects.create_user("rep1")
        user_sr2 = User.objects.create_user("rep2")
        user_sr3 = User.objects.create_user("rep3")
        self.sm = models.Employee.objects.create(
            user=user_sm,
            position=models.Position.store_manager()
        )
        self.asm = models.Employee.objects.create(
            user=user_asm,
            position=models.Position.assistant_store_manager()
        )
        self.sr1 = models.Employee.objects.create(
            user=user_sr1,
            position=models.Position.sales_rep()
        )
        self.sr2 = models.Employee.objects.create(
            user=user_sr2,
            position=models.Position.sales_rep()
        )
        self.sr3 = models.Employee.objects.create(
            user=user_sr3,
            position=models.Position.sales_rep()
        )

    def test_schedule_week(self):
        day = datetime.date.today()
        tasks.schedule_week(day)
        self.assertFalse(models.Shift.objects.filter(date=day).count() == 0)


