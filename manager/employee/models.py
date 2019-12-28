"""
Employee Models
===============
"""
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.urls import reverse


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


class EmployeeQuerySet(models.QuerySet):

    def active(self):
        return self.filter(status='active')

    def inactive(self):
        return self.filter(status='inactive')

    def managers(self):
        return self.filter(
            Q(position=Position.store_manager()) |
            Q(position=Position.assistant_store_manager())
        )

    def store_manager(self):
        return self.filter(
            status='active',
            position=Position.store_manager()
        )

    def assistant_store_manager(self):
        return self.filter(
            status='active',
            position=Position.assistant_store_manager()
        )

    def sales_reps(self):
        return self.filter(
            status='active',
            position=Position.sales_rep()
        )


class EmployeeManager(models.Manager):

    def get_queryset(self):
        return EmployeeQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def inactive(self):
        return self.get_queryset().inactive()

    def managers(self):
        return self.get_queryset().managers()

    def store_manager(self):
        return self.get_queryset().store_manager()

    def assistant_store_manager(self):
        return self.get_queryset().assistant_store_manager()

    def sales_reps(self):
        return self.get_queryset().sales_reps()

    def create_employee(self,
                        username,
                        email=None,
                        password=None,
                        position=None,
                        status='active',
                        **extra_fields):
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **extra_fields
        )
        if not position:
            position = Position.sales_rep()
        return self.create(
            user=user,
            position=position,
            status=status
        )


class Employee(models.Model):
    objects = EmployeeManager()
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

    def get_absolute_url(self):
        return reverse('employee:employee-edit', kwargs={'pk': self.id})

    @staticmethod
    def store_manager():
        try:
            return Employee.objects.get(position=Position.store_manager())
        except Employee.DoesNotExist:
            return None

    @staticmethod
    def asm():
        try:
            return Employee.objects.get(position=Position.assistant_store_manager())
        except Employee.DoesNotExist:
            return None

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
