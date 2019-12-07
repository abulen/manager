from django.contrib import admin
from . import models
# Register your models here.


@admin.register(models.Employee)
class EmployeeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Position)
class PositionAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Day)
class DayAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Shift)
class ShiftAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Week)
class WeekAdmin(admin.ModelAdmin):
    pass

