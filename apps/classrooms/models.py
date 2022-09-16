from pyexpat import model
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.template.defaultfilters import slugify

User = get_user_model()


def get_first_name(self):
    return self.first_name


User.add_to_class("__str__", get_first_name)


class Classroom(models.Model):
    grade = models.CharField(max_length=40)
    homeroom_teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="wali_kelas"
    )
    student = models.ManyToManyField(User, related_name="kelasku")

    def __str__(self):
        return self.grade

    class Meta:
        verbose_name_plural = "Kelas"


class ClassroomSubject(models.Model):
    name = models.CharField(max_length=40)
    slug = models.SlugField(null=True, blank=True, unique=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pengajar")
    classroom = models.ForeignKey(
        Classroom, on_delete=models.CASCADE, related_name="subjects"
    )

    def save(self, *args, **kwargs):
        if self.slug == None:
            self.slug = slugify(
                f"{self.name} {self.classroom.grade} {self.teacher.first_name}"
            )
        super(ClassroomSubject, self).save(*args, **kwargs)

    def __str__(self):
        return self.name + " - " + self.classroom.grade

    class Meta:
        verbose_name_plural = "Mata Pelajaran"


STATUS = (
    ("ALPHA", "alpha"),
    ("HADIR", "hadir"),
    ("IJIN", "ijin"),
)


class ClassroomTimetable(models.Model):
    grade = models.CharField(max_length=200, null=True)
    token = models.CharField(max_length=4, blank=True, null=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True)
    subject = models.ForeignKey(ClassroomSubject, on_delete=models.CASCADE, null=True)

    def populate(self, *args, **kwargs):
        print("checking")
        for student in self.subject.classroom.student.all():
            if (
                not ClassroomAttendance.objects.filter(timetable__id=self.id)
                .filter(student=student)
                .exists()
            ):
                obj = ClassroomAttendance.objects.create(
                    student=student, status="ALPHA", timetable=self
                )
                obj.save()
            else:
                print("sudah ada")

    def fill_grade(self, *args, **kwargs):
        self.grade = self.subject.classroom.grade
        ClassroomTimetable.save(*args, **kwargs)

    def __str__(self):
        return "{} | {}".format(self.subject.teacher.first_name, self.subject.name)

    class Meta:
        ordering = ("-id",)
        verbose_name_plural = "Jadwal Kelas"


class ClassroomAttendance(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=10)
    status = models.CharField(default="ALPHA", choices=STATUS, max_length=20)
    timetable = models.ForeignKey(ClassroomTimetable, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return "{} {}".format(self.student.username, self.status)

    class Meta:
        verbose_name_plural = "Kehadiran Kelas"


class ClassroomJournal(models.Model):
    subject_grade = models.ForeignKey(
        ClassroomSubject, on_delete=models.CASCADE, blank=True, null=True
    )
    timetable = models.ForeignKey(ClassroomTimetable, on_delete=models.CASCADE)
    description = models.TextField()

    def save(self, *args, **kwargs):
        self.subject_grade = self.timetable.subject
        super(ClassroomJournal, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return "Jurnal id {}".format(self.id)
