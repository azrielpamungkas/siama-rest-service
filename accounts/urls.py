from django.urls import path
from .views import auth_token
from apps.attendances.views import LeaveView

urlpatterns = [
    path("v1/obtain-token/", auth_token),
    path("v1/leave/", LeaveView.as_view()),
]
