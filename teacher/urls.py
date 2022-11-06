from django.urls import path
from . import views


urlpatterns = [
    path("v1/teacher/c/<int:pk>/", views.TeacherClassroomDetail.as_view()),
    path("v1/teacher/class/", views.TeacherClassroomList.as_view()),
    path("v1/teacher/info/", views.teacher_account),
    path("v1/teacher/schedule/", views.TeacherSchedule.as_view()),
    path("v1/teacher/create-journal/", views.teacher_journal),
    path("v1/teacher/journal/", views.teacher_journal_list),
]
