from django.urls import path, include
from schedule import views

app_name = 'schedule'

urlpatterns = [
    path('',
         views.CalendarIndexView.as_view(),
         name='calendar-index'
         ),
    path('schedule/',
         views.ScheduleView.as_view(),
         name='schedule'
         ),
    path('schedule/google-sync/',
         views.google_sync,
         name='google-sync'),
    path('shift/create/',
         views.CreateShiftView.as_view(),
         name='shift-create'),
    path('shift/<int:pk>/',
         views.EditShiftView.as_view(),
         name='shift-edit'),
    path('shift/<int:pk>/delete/',
         views.DeleteShiftView.as_view(),
         name='shift-delete'),
    path('shift/last/', views.last_scheduled_day,
         name='shift-last'),
    path('schedule/create/',
         views.create_schedule,
         name='schedule-create'),
    path('ssw/create/',
         views.create_ssw,
         name='ssw-create'),
    path('leave/create/',
         views.create_leave,
         name='leave-create'),
]