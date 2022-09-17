from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView

from apps.classrooms.models import ClassroomTimetable
from . import serializers
from utils.gps import detector, validation
from .models import Attendance, AttendanceTimetable, Leave
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
import datetime
from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, FormParser
from .docs import AttendanceDoc

doc = AttendanceDoc()

# /v1/teacher/?geo=${user.latitude},${user.longitude}


class LeaveView(CreateAPIView):
    queryset = ""

    def get(self, request):
        classroom_timetable_q = ClassroomTimetable.objects.all().filter(
            date=datetime.date.today(), subject__classroom__student=request.user.id
        )
        print(classroom_timetable_q)

        if request.user.groups.filter(name="student").exists():
            role = "MRD"
        elif request.user.groups.filter(name="teacher").exists():
            role = "GRU"
        else:
            role = "KRY"

        attendance_timetable_q = AttendanceTimetable.objects.filter(role=role)
        res = {
            "history": {},
            "attendanceTimetable": [
                {"id": data.id, "name": data.__str__()}
                for data in attendance_timetable_q
            ],
            "classroomTimetable": [
                {"id": data.id, "name": data.__str__()}
                for data in classroom_timetable_q
            ],
        }

        queryset = Leave.objects.filter(user=request.user.id).order_by("-id")
        print(queryset)
        for q in queryset:
            month_year = "{} {}".format(q.created_at.strftime("%b"), q.created_at.year)
            print(month_year)
            res["history"].setdefault(month_year, [])
            res["history"][month_year].append(
                {
                    "type": (lambda x: "Sakit" if x else "Ijin")(q.leave_type),
                    "img" : q.attachment.url,
                    "mode": (lambda x: "Full Day" if x else "Half Day")(q.leave_mode),
                    "reason": q.reason,
                    "status": (
                        lambda x: "Approved"
                        if x
                        else ("Sedang menunggu" if x == None else "Ditolak")
                    )(q.approve),
                    "status_code": (lambda x: 1 if x else (3 if x == None else 0))(
                        q.approve
                    ),
                    "date": q.created_at.strftime("%d %B %Y"),
                }
            )
        return Response(res)

    # def post(self, request, *args, **kwargs):
    #     print("request post: ", request.data)
    #     return super().post(request, *args, **kwargs)

    def get_serializer_class(self, *args, **kwargs):
        if self.request.GET.get("type") == "half":
            return serializers.LeaveHalfSer
        else:
            return serializers.LeaveFullSer

    def perform_create(self, serializer):
        if self.request.GET.get("type") == "half":
            leave_mode = 0
        else:
            leave_mode = 1
        serializer.save(user=self.request.user, leave_mode=leave_mode)


class AttendanceView(APIView):
    greeting = "Selamat Pagi"
    roles = {"teacher": "GRU", "student": "MRD", "staff": "KWN"}

    def get(self, request):
        group = request.user.groups.filter().first().name
        attendance_timetable = (
            AttendanceTimetable.objects.filter(date=datetime.date.today())
            .filter(role=self.roles[group])
            .first()
        )
        if attendance_timetable:
            attendance = Attendance.objects.filter(
                user=request.user, timetable=attendance_timetable.id
            ).first()

        res = {
            "greet": self.greeting,
            "work_time": (
                lambda x: None if x is None else x.work_time.strftime("%H:%M")
            )(attendance_timetable),
            "home_time": (
                lambda x: None if x is None else x.home_time.strftime("%H:%M")
            )(attendance_timetable),
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

        # for activate button
        if attendance_timetable:
            if attendance != None:
                if attendance.clock_out == None:
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

    def post(self, request):
        group = request.user.groups.filter().first().name
        # GET Timetable for attendance
        attendance = (
            AttendanceTimetable.objects.filter(date=datetime.date.today())
            .filter(role=self.roles[group])
            .first()
        )
        obj = Attendance.objects.filter(
            user=request.user, timetable=attendance.id
        ).first()
        time = datetime.datetime.now().time()

        if True:
            if obj:
                if obj.clock_in != None and obj.clock_out == None:
                    if attendance.home_time <= time:
                        obj.clock_out = time
                        obj.save()
                        response = {
                            "activity": {
                                "type": "clock out",
                                "time": f"{time.hour}:{time.minute}",
                            },
                            "status_button": {"clockIn": False, "clockOut": False},
                            "success": {"message": "Anda berhasil clock out"},
                        }
                        return Response(response)
                    return Response(
                        {
                            "error": {
                                "message": "Anda belum bisa clock out untuk saat ini"
                            },
                        }
                    )
                return Response(
                    {
                        "error": {
                            "message": "Anda sudah melakukan prensensi untuk saat ini"
                        },
                    }
                )
            else:
                if True:
                    Attendance.objects.create(
                        user=User.objects.get(id=request.user.id),
                        timetable=AttendanceTimetable.objects.get(id=attendance.id),
                        clock_in=time,
                        status=(lambda x: "H" if x <= attendance.work_time else "T")(
                            time
                        ),
                    )
                    response = {
                        "activity": {
                            "type": "clock in",
                            "time": f"{time.hour}:{time.minute}",
                        },
                        "status_button": {"clockIn": False, "clockOut": True},
                        "success": {"message": "Anda berhasil clock in"},
                    }
                    return Response(response)
        return Response(
            {
                "error": {"message": "Anda diluat titik point!"},
            }
        )
