from django.urls import path, include
from schedule import views

app_name = 'schedule'

urlpatterns = [
    path('',
         views.CalendarIndexView.as_view(),
         name='calendar-index'
         ),
]