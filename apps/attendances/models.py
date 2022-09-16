from django.db import models
from django.contrib.auth.models import User
from apps.classrooms.models import ClassroomSubject, ClassroomTimetable


class AttendanceTimetable(models.Model):
    class RoleInSchool(models.TextChoices):
        STUDENT = "MRD", "Student"
        STAFF = "KWN", "Staff"
        TEACHER = "GRU", "Teacher"
        STUDENT_HOME = "MRD_HOME", "Student Home"
        STAFF_HOME = "KWN_HOME", "Staff Home"
        TEACHER_HOME = "GRU_HOME", "Teacher Home"

    date = models.DateField()
    work_time = models.TimeField()
    home_time = models.TimeField()
    role = models.CharField(choices=RoleInSchool.choices, max_length=20)

    def __str__(self):
        return f"{self.date.strftime('%b %d, %Y')}"

    class Meta:
        verbose_name_plural = "Penjadwalan Umum"


class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    clock_in = models.TimeField(null=True, blank=True)
    clock_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20)
    timetable = models.ForeignKey(AttendanceTimetable, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Daftar Hadir"


class Leave(models.Model):
    LEAVE_TYPE_CHOICHES = [
        (0, "Ijin"),
        (1, "Sakit"),
    ]

    LEAVE_MODE_CHOICHES = [
        (0, "Full"),
        (1, "Half"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    leave_mode = models.SmallIntegerField(blank=True)
    leave_type = models.SmallIntegerField(blank=True)
    attendance_scheduled = models.ManyToManyField(AttendanceTimetable, blank=True)
    classroom_scheduled = models.ManyToManyField(ClassroomTimetable, blank=True)
    reason = models.TextField()
    attachment = models.ImageField()
    approve = models.BooleanField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + " " + self.reason

    # def save(self, *args, **kwargs):
    #     # if self.approve == True:
    #     #     if self.leave_mode == 0:
    #     #         self.attendance_scheduled.
    #     # pass
    #     print(self.attendance_scheduled)
    #     super().save(*args, **kwargs)
