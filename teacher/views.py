import datetime
from django.core.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from apps.classrooms.models import (
    Classroom,
    ClassroomAttendance,
    ClassroomJournal,
    ClassroomSubject,
    ClassroomTimetable,
)
from apps.attendances.models import AttendanceTimetable, Attendance
from teacher.serializers import (
    TeacherJournalSerializer,
    TeacherClassroomSerializer,
    TeacherClassroomDetailSerializer,
)
from utils.gps import detector
from utils.shortcuts import current_lecture_teacher
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics

from rest_framework import permissions


class TeacherOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name="teacher").exists():
            return True
        return False


class TeacherClassroomList(generics.ListAPIView):
    queryset = ClassroomSubject.objects.all()
    serializer_class = TeacherClassroomSerializer
    permission_classes = [TeacherOnly]

    def get_queryset(self):
        return ClassroomSubject.objects.filter(teacher=self.request.user.id)


class TeacherClassroomDetail(generics.RetrieveAPIView):
    queryset = ClassroomSubject.objects.all()
    serializer_class = TeacherClassroomDetailSerializer
    lookup_field = "pk"
    permission_classes = [TeacherOnly]

@api_view(["GET"])
@permission_classes([TeacherOnly])
def teacher_journal_list(request):
    res = []
    subject_id = request.GET.get("id")
    obj = ClassroomJournal.objects.filter(subject_grade=subject_id).filter(
        subject_grade__teacher=request.user.id
    )
    if obj.count() != 0:
        for journal in obj:
            res.append(
                {
                    "description": journal.description,
                    "date": journal.timetable.date.strftime("%d %B, %Y"),
                }
            )
        return Response(res)
    return Response(res)


@api_view(["GET", "POST"])
@permission_classes([TeacherOnly])
def teacher_journal(request):
    current_class = (
        ClassroomTimetable.objects.all()
        .filter(date=datetime.date.today())
        .filter(start_time__lte=datetime.datetime.now().time())
        .filter(end_time__gt=datetime.datetime.now().time())
        .filter(subject__teacher=request.user.id)
    )
    if current_class.count() != 0:
        c = current_class.first()
        if not ClassroomJournal.objects.filter(timetable=c).exists():
            if request.method == "POST":
                serializer = TeacherJournalSerializer(data=request.data)
                if serializer.is_valid():
                    obj = ClassroomJournal.objects.create(
                        timetable=c,
                        description=serializer.data["description"],
                    )
                    obj.save()
                    return Response("valid")
                return Response(
                    serializer.errors,
                )
            return Response(
                {
                    "subject": c.subject.name,
                    "grade": c.subject.classroom.grade,
                }
            )
        return Response(
            {"message": "Hanya dapat input jurnal satu kali"},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )
    return Response(None)


@api_view(["GET"])
@permission_classes([TeacherOnly])
def teacher_account(request):
    res = {
        "user": {
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "username": request.user.username,
        },
        "classrooms": [],
    }
    obj = ClassroomSubject.objects.filter(teacher=request.user.id)
    if obj:
        for sub in obj:
            res["classrooms"].append(
                {
                    "subject": sub.name,
                    "grade": sub.classroom.grade,
                }
            )
        return Response(res)
    return Response(res)


class TeacherSchedule(APIView):
    permission_classes = [TeacherOnly]

    def get(self, request):
        clasroom_timetable_qry = ClassroomTimetable.objects.all().filter(
            subject__teacher=request.user.id
        )
        res = {}
        for obj in clasroom_timetable_qry:
            res.setdefault(obj.date.strftime("%-m/%-d/%Y"), [])
            res[obj.date.strftime("%-m/%-d/%Y")].append(
                {
                    "id": obj.subject.id,
                    "token": obj.token,
                    "on_going": (
                        lambda x, y: False
                        if y == None
                        else (True if x == y.id else False)
                    )(
                        obj.id,
                        current_lecture_teacher(request.user.id, ClassroomTimetable),
                    ),
                    "subject": obj.subject.name,
                    "classroom": obj.subject.classroom.grade,
                    "teacher": {
                        "first_name": obj.subject.teacher.first_name,
                        "last_name": obj.subject.teacher.last_name,
                    },
                    "start_time": obj.start_time.strftime("%H:%M"),
                    "end_time": obj.end_time.strftime("%H:%M"),
                }
            )
        return Response(res)


class DetailPresence(APIView):
    permission_classes = [TeacherOnly]

    def get_student_attendace():
        obj = ClassroomAttendance.objects.get(timetable=id)
        return obj

    def get(self, request):
        obj = (
            ClassroomTimetable.objects.filter(date=datetime.date.today())
            .filter(start_time__lte=datetime.datetime.now().time())
            .filter(end_time__gt=datetime.datetime.now().time())
            .filter(subject__teacher=request.user.id)
            .first()
        )

        if obj:
            res = {
                "name": obj.subject.name,
                "teacher": f"{obj.subject.teacher.first_name}",
                "classroom": obj.subject.classroom.grade,
                "time": f"{obj.start_time.strftime('%H:%M')} - {obj.end_time.strftime('%H:%M')} WIB",
                "students": [],
            }
            for student in ClassroomAttendance.objects.filter(timetable=obj.id):
                res["students"].append(
                    {
                        "name": f"{student.student.first_name}",
                        "status": f"{student.status}",
                    }
                )
            return Response(res)
        return Response(
            {
                "name": None,
                "teacher": None,
                "classroom": None,
                "time": None,
                "students": [],
            }
        )


# @api_view(["GET"])
# def teacher_classroom_detail(request):
#     subject_id = request.GET.get("id")
#     obj = ClassroomAttendance.objects.filter(
#         timetable__subject=subject_id, timetable__date__lte=datetime.date.today()
#     )
#     students = Classroom.objects.get(
#         id=obj.first().timetable.subject.classroom.id
#     ).student.all()
#     if obj.count() != 0:
#         res = {
#             "subject": obj.first().timetable.subject.name,
#             "grade": obj.first().timetable.subject.classroom.grade,
#             "students": [],
#             "date": {},
#         }
#         for student in students:
#             res["students"].append(student.first_name)

#         for data in obj:
#             d = data.timetable.date.strftime("%A, %-d %B %Y")
#             res["date"].setdefault(d, [])
#             res["date"][d].append(
#                 {
#                     "name": data.student.first_name + " " + data.student.last_name,
#                     "status": data.status,
#                 }
#             )
#         return Response(res)
#     return Response({})
