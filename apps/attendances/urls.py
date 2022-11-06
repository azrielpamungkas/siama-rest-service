from django.urls import path
from . import views

urlpatterns = [
    path("v1/general-attendance/", views.AttendanceView.as_view()),
    path("v1/attendance/", views.attendance_view, name="attendance"),
    path("v1/activity/", views.activity),
]
