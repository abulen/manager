from django.test import TestCase
from django.contrib.auth.models import User
from . import models


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
        self.sm = models.Employee.objects.create_employee(
            "sm",
            None,
            None,
            models.Position.store_manager()
        )
        self.asm = models.Employee.objects.create_employee(
            "asm",
            None,
            None,
            models.Position.assistant_store_manager()
        )
        self.sr = models.Employee.objects.create_employee(
            "rep",
            None,
            None,
            models.Position.sales_rep()
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
