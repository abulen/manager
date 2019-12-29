from django.urls import path, include
from employee import views

app_name = 'employee'

urlpatterns = [
    path('',
         views.EmployeeListView.as_view(),
         name='employee-list'
         ),
    path('edit/<int:pk>/',
         views.EmployeeEditView.as_view(),
         name='employee-edit'
         ),
    path('create',
         views.EmployeeView.as_view(),
         name='create-employee'
         ),
]
