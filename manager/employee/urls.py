from django.urls import path, include
from employee import views

app_name = 'employee'

urlpatterns = [
    path('create',
         views.EmployeeView.as_view(),
         name='create-employee'
         ),
]
