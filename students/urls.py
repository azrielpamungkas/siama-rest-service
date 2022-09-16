from django.urls import path
from students import views


urlpatterns = [
    path("v1/student/schedule/", views.StudentSchedule.as_view()),
    path("v1/student/history/", views.StudentHistory.as_view()),
    path("v1/student/submit/", views.StudentPresence.as_view()),
    path("v1/student/statistic/", views.StudentStatistic.as_view()),
]
