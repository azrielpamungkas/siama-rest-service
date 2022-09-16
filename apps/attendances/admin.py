from django.contrib import admin
from .models import Attendance, AttendanceTimetable, Leave
# Register your models here.
admin.site.register(Attendance)
admin.site.register(AttendanceTimetable)
admin.site.register(Leave)
