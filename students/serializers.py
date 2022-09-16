from dataclasses import field
from rest_framework import serializers
from apps.classrooms.models import ClassroomAttendance, ClassroomTimetable
import datetime


class StudentPresenceSer(serializers.ModelSerializer):
    class Meta:
        model = ClassroomAttendance
        fields = (
            "token",
            "timetable",
        )

    def perform_create(self, serializer):
        serializer.save()

    def create(self, validated_data):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        data = validated_data.copy()
        data["student"] = user
        data["status"] = "HADIR"
        timetable = data["timetable"]
        token = data.pop("token")
        if (
            ClassroomAttendance.objects.filter(timetable=timetable)
            .filter(student=user)
            .exists()
        ):
            raise serializers.ValidationError(
                "Anda Sudah Melakukan Presensi Pada Jam Ini"
            )
        timetable_token = ClassroomTimetable.objects.get(id=timetable.id).token
        if token != timetable_token:
            raise serializers.ValidationError("Token Anda Salah")
        return super(StudentPresenceSer, self).create(data)

    def check_permissions(self):
        if self.request.user.groups.filter(name="student").exists:
            return True
        else:
            return False

    # def to_representation(self, instance):
    #     data = super(serializers.ModelSerializer, self).to_representation(instance)
    #     timetable_query = ClassroomTimetable.objects.filter(
    #         date=datetime.date.today()
    #     ).filter(subject__classroom__student=request.user.id)
    #     timetable = []
    #     for t in timetable_query:
    #         timetable.append({"id": t.id, "name": f"{timetable.subject.name}"})
    #     return "Hello World"
