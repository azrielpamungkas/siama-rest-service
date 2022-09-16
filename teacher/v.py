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
from teacher.serializers import TeacherJournalSerializer
from utils.gps import detector
from utils.shortcuts import current_lecture_teacher
from rest_framework.decorators import api_view

# Teacher/class
@api_view(["GET"])
def teacher_classroom(request):
    res = {
        "classrooms": [],
    }

    subject_queryset = ClassroomSubject.objects.filter(teacher=request.user.id)
    print(subject_queryset)
    if subject_queryset:
        for q in subject_queryset:
            res["classrooms"].append(
                {
                    "id": q.id,
                    "subject": q.name,
                    "grade": q.classroom.grade,
                }
            )
    return Response(res)


@api_view(["GET"])
def teacher_activity(request):
    res = []
    datenow = datetime.datetime.now().date()
    year = datenow.year
    month = datenow.month

    obj = Attendance.objects.filter(
        timetable__date__year__gte=year,
        timetable__date__month__gte=month,
        timetable__date__year__lte=year,
        timetable__date__month__lte=month,
    )

    for day in range(datenow.min.day, datenow.max.day):
        if obj.filter(timetable__date__day=day).exists():
            attendance = obj.get(timetable__date__day=day)
            history = {
                "day": day,
                "clock_in": attendance.clock_in.strftime("%H:%M"),
                "clock_out": attendance.clock_out.strftime("%H:%M"),
                "status": attendance.status,
            }
        else:
            history = {
                "day": day,
                "clock_in": "-",
                "clock_out": "-",
                "status": "off",
            }
        res.append(history)
    return Response(res)


@api_view(["GET"])
def teacher_journal_list(request):
    res = []
    subject_id = request.GET.get("id")
    print(subject_id, type(subject_id))
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
def teacher_classroom_detail(request):
    subject_id = request.GET.get("id")
    obj = ClassroomAttendance.objects.filter(timetable__subject=subject_id)
    if obj.count() != 0:
        res = {
            "subject": obj.first().timetable.subject.name,
            "grade": obj.first().timetable.subject.classroom.grade,
            "date": {},
        }
        for data in obj:
            d = data.timetable.date.strftime("%A, %-d %B %Y")
            res["date"].setdefault(d, [])
            res["date"][d].append(
                {
                    "name": data.student.first_name + " " + data.student.last_name,
                    "status": data.status,
                }
            )
        return Response(res)
    return Response({})


@api_view(["GET"])
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


class TeacherDashboard(APIView):
    if datetime.datetime.now().hour < 12:
        greeting = "Selamat Pagi"
    elif datetime.datetime.now().hour < 15:
        greeting = "Selamat Siang"
    elif datetime.datetime.now().hour < 18:
        greeting = "Selamat Sore"
    else:
        greeting = "Selamat Malam"

    def get(self, request):
        attendance_timetable_obj = (
            AttendanceTimetable.objects.filter(date=datetime.datetime.today().date())
            .filter(role="GRU")
            .first()
        )
        if request.user.groups.filter(name="teacher").exists():
            res = {
                "greet": self.greeting,
                "work_time": (
                    lambda x: None if x is None else x.work_time.strftime("%H:%M")
                )(attendance_timetable_obj),
                "home_time": (
                    lambda x: None if x is None else x.home_time.strftime("%H:%M")
                )(attendance_timetable_obj),
                "user": {
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name,
                    "address": detector(geo=self.request.query_params.get("geo")),
                },
                "recent_activity": [],
                "status_button": {
                    "clockIn": False,
                    "clockOut": False,
                },
                "message": "",
            }

            if attendance_timetable_obj != None:
                user_attendance = (
                    Attendance.objects.filter(user=request.user.id)
                    .filter(timetable=attendance_timetable_obj.id)
                    .first()
                )
                if user_attendance != None:
                    if user_attendance.clock_out == None:
                        res["status_button"]["clockOut"] = True
                    else:
                        res["status_button"]["clockIn"] = False
                        res["status_button"]["clockOut"] = False
                else:
                    res["status_button"]["clockIn"] = True

            data = []
            for attendance in Attendance.objects.filter(user=request.user.id):
                if attendance.clock_in != None:
                    data.append(["clock in", attendance.clock_in])
                if attendance.clock_out != None:
                    data.append(["clock out", attendance.clock_out])

            if len(data) != 0:
                data.reverse()
                for d in data[:4]:
                    res["recent_activity"].append(
                        {"type": d[0], "time": d[1].strftime("%H:%M")}
                    )
                return Response(res)
            return Response(res)

        raise PermissionDenied

    def post(self, request):
        attendance_timetable_obj = (
            AttendanceTimetable.objects.filter(date=datetime.datetime.today().date())
            .filter(role="GRU")
            .first()
        )
        if request.user.groups.filter(name="teacher").exists():
            res = {
                "greet": self.greeting,
                "work_time": (
                    lambda x: None if x is None else x.work_time.strftime("%H:%M")
                )(attendance_timetable_obj),
                "home_time": (
                    lambda x: None if x is None else x.home_time.strftime("%H:%M")
                )(attendance_timetable_obj),
                "user": {
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name,
                    "address": detector(geo=self.request.query_params.get("geo")),
                },
                "recent_activity": [],
                "status_button": {
                    "clockIn": False,
                    "clockOut": False,
                },
                "message": "",
            }

            if attendance_timetable_obj != None:
                user_attendance = (
                    Attendance.objects.filter(user=request.user.id)
                    .filter(timetable=attendance_timetable_obj.id)
                    .first()
                )
                if user_attendance != None:
                    if user_attendance.clock_out == None:
                        res["status_button"]["clockOut"] = True
                    else:
                        res["status_button"]["clockIn"] = False
                        res["status_button"]["clockOut"] = False
                else:
                    res["status_button"]["clockIn"] = True

            data = []
            for attendance in Attendance.objects.filter(user=request.user.id):
                if attendance.clock_in != None:
                    data.append(["clock in", attendance.clock_in])
                if attendance.clock_out != None:
                    data.append(["clock out", attendance.clock_out])

            if len(data) != 0:
                for d in data:
                    res["recent_activity"].append(
                        {"type": d[0], "time": d[1].strftime("%H:%M")}
                    )
                return Response(res)
            return Response(res)
        raise PermissionDenied


class TeacherSchedule(APIView):
    def get(self, request):
        clasroom_timetable_qry = ClassroomTimetable.objects.filter(
            subject__teacher=request.user.id
        )
        res = {}
        for obj in clasroom_timetable_qry:
            res.setdefault(obj.date.strftime("%-m/%-d/%Y"), [])
            res[obj.date.strftime("%-m/%-d/%Y")].append(
                {
                    "id": obj.id,
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
                    "start_time": obj.start_time,
                    "end_time": obj.end_time,
                }
            )
        return Response(res)


class DetailPresence(APIView):
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
