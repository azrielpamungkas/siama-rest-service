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

@api_view(["GET"])
def staff_activity(request):
    res = []
    datenow = datetime.datetime.now().date()
    year = datenow.year
    month = datenow.month

    obj = Attendance.objects.filter(user=request.user.id).filter(
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
                "clock_in": (lambda x: x.strftime("%H:%M:%S") if x is not None else "-")(attendance.clock_in),
                "clock_out": (lambda x: x.strftime("%H:%M:%S") if x is not None else "-")(attendance.clock_out),
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
def staff_account(request):
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


class StaffDashboard(APIView):
    if datetime.datetime.now().hour < 12:
        greeting = "Selamat Pagi"
    elif datetime.datetime.now().hour < 15:
        greeting = "Selamat Siang"
    elif datetime.datetime.now().hour < 18:
        greeting = "Selamat Sore"
    elif datetime.datetime.now().hour < 23:
        greeting = "Selamat Malam"
    else:
        greeting = "Selamat Pagi"

    def get(self, request):
        attendance_timetable_obj = (
            AttendanceTimetable.objects.filter(date=datetime.datetime.today().date())
            .filter(role="KWN")
            .first()
        )
        if request.user.groups.filter(name="staff").exists():
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
            .filter(role="KWN")
            .first()
        )
        if request.user.groups.filter(name="staff").exists():
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



