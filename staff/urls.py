from django.urls import path
from . import views


urlpatterns = [
    path("v1/staff/", views.StaffDashboard.as_view()),
    path("v1/staff/info/", views.staff_account),
    path("v1/staff/activity", views.staff_activity),

]
