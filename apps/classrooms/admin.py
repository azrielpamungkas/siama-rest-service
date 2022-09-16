from django.contrib import admin
from .models import (
    Classroom,
    ClassroomJournal,
    ClassroomSubject,
    ClassroomTimetable,
    ClassroomAttendance,
)

class ClassroomAdmin(admin.ModelAdmin):
    # list_filter = ('teacher__username',)
    list_max_show_all = 500
    search_fields = ['grade','student__first_name']


# Register your models here.
admin.site.register(Classroom, ClassroomAdmin)
admin.site.register(ClassroomSubject)
admin.site.register(ClassroomTimetable)
admin.site.register(ClassroomAttendance)
admin.site.register(ClassroomJournal)
