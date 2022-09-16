from rest_framework import serializers
from apps.classrooms import models


class TeacherJournalSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=240)

    class Meta:
        fields = "__all__"


class TeacherClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ClassroomSubject
        fields = "__all__"

    def to_representation(self, instance):
        data = super(serializers.ModelSerializer, self).to_representation(instance)
        subject = data.pop("name")
        grade = models.Classroom.objects.get(id=data["classroom"]).grade
        data["subject"] = subject
        data["grade"] = grade
        return data

        def check_permissions(self):
            return False


class TeacherClassroomDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ClassroomSubject
        fields = "__all__"

    def to_representation(self, instance):
        data = super(serializers.ModelSerializer, self).to_representation(instance)
        subject = data.pop("name")
        grade = models.Classroom.objects.get(id=data["classroom"]).grade
        data["subject"] = subject
        data["grade"] = grade
        id = data["id"]
        students_query = models.ClassroomSubject.objects.get(
            id=id
        ).classroom.student.all()

        students = [student.first_name for student in students_query]
        data["students"] = students

        classroom_timetable_query = models.ClassroomTimetable.objects.filter(
            subject__id=id
        )
        # {"tanggal": ["nama", "status"]}
        timetable_dict = {}
        for timetable in classroom_timetable_query:
            timetable_dict.setdefault(f"{timetable.date}", [])
            for student in students:
                if (
                    models.ClassroomAttendance.objects.filter(timetable=timetable)
                    .filter(student__first_name=student)
                    .exists()
                ):
                    status = (
                        models.ClassroomAttendance.objects.filter(timetable=timetable)
                        .get(student__first_name=student)
                        .status
                    )
                else:
                    status = "ALPHA"
                timetable_dict[f"{timetable.date}"].append(
                    {"name": student, "status": status}
                )
        data["date"] = timetable_dict
        return data

        def check_permissions(self):
            return False
