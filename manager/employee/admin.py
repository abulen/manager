from django.contrib import admin
from . import models
# Register your models here.


@admin.register(models.Employee)
class EmployeeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Position)
class PositionAdmin(admin.ModelAdmin):
    pass
