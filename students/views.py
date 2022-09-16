import datetime
from django.core.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from students.serializers import StudentPresenceSer
from utils.gps import validation, detector
from utils.shortcuts import current_lecture, auto_now
from apps.classrooms.models import ClassroomTimetable, ClassroomAttendance
from apps.attendances.models import AttendanceTimetable, Attendance
from drf_yasg.utils import swagger_auto_schema

from rest_framework import permissions


class StudentOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name="student").exists():
            return True
        return False


class StudentSchedule(APIView):
    permission_classes = [StudentOnly]

    def get(self, request):
        clasroom_timetable_qry = ClassroomTimetable.objects.all().filter(
            subject__classroom__student=request.user.id
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
                    )(obj.id, current_lecture(request.user.id, ClassroomTimetable)),
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


class StudentPresence(generics.ListCreateAPIView):
    queryset = ClassroomAttendance.objects.all()
    permission_classes = [StudentOnly]
    serializer_class = StudentPresenceSer

    def list(self, request, *args, **kwargs):
        response = super(StudentPresence, self).list(request, args, kwargs)
        response.data = {"timetable": []}
        timetable_query = ClassroomTimetable.objects.filter(
            date=datetime.date.today()
        ).filter(subject__classroom__student=request.user.id)
        for t in timetable_query:
            response.data["timetable"].append(
                {
                    "id": t.id,
                    "name": f"{t.subject.name} - {t.subject.teacher.first_name}",
                }
            )
        return response


class StudentHistory(APIView):
    permission_classes = [StudentOnly]

    def get(self, request):
        lecture_histories = (
            ClassroomAttendance.objects.all()
            .filter(student=request.user.id)
            .filter(timetable__date__lte=datetime.date.today())
        )
        if lecture_histories != None:
            res = {
                "user": {
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name,
                    "username": request.user.username,
                }
            }
            for history in lecture_histories:
                month_year = "{} {}".format(
                    history.timetable.date.strftime("%b"), history.timetable.date.year
                )
                res.setdefault(month_year, [])
                res[month_year].append(
                    {
                        "name": history.timetable.subject.name,
                        "date": history.timetable.date,
                        "status": history.status,
                    }
                )
            return Response(res)
        return Response()


class StudentStatistic(APIView):
    permission_classes = [StudentOnly]

    def get(self, request):
        timetable_cnt = ClassroomTimetable.objects.filter(
            date__lte=auto_now("today")
        ).count()
        attendance_qry = ClassroomAttendance.objects.filter(
            student=request.user.id
        ).filter(timetable__date__lte=auto_now("today"))
        try:
            res = {
                "leave": attendance_qry.filter(status="IJIN").count()
                / attendance_qry.count(),
                "absent": attendance_qry.filter(status="ALPHA").count()
                / attendance_qry.count(),
                "presence": attendance_qry.filter(status="HADIR").count()
                / attendance_qry.count(),
                "sick": attendance_qry.filter(status="SAKIT").count()
                / attendance_qry.count(),
                "indicator": (
                    lambda x: "Aman" if x > 0.8 else ("Rawan" if x > 0.7 else "Bahaya")
                )(attendance_qry.filter(status="HADIR").count()),
            }
        except:
            res = {
                "leave": 0,
                "absent": 0,
                "presence": 1,
                "sick": 0,
                "indicator": "Belum Ada Data",
            }
        return Response(res)


# class StudentPresence(APIView):
#     queryset = ClassroomTimetable.objects.all()
#     serializer_class = StudentPresenceSer

#     def get_queryset(self):
#         return super().get_queryset().filter(id=1)

#     def get(self, request):
#         scheduled_obj = current_lecture(request.user.id, ClassroomTimetable)
#         if scheduled_obj:
#             class_time = "{} - {} WIB".format(
#                 scheduled_obj.start_time.strftime("%H:%M"),
#                 scheduled_obj.end_time.strftime("%H:%M"),
#             )
#             teacher_name = "{} {}".format(
#                 scheduled_obj.subject.teacher.first_name,
#                 scheduled_obj.subject.teacher.last_name,
#             )
#             res = {
#                 "is_attended": False,
#                 "name": scheduled_obj.subject.name,
#                 "teacher": teacher_name,
#                 "time": class_time,
#                 "user": {"address": detector(geo=self.request.query_params.get("geo"))},
#             }
#             student_obj = ClassroomAttendance.objects.filter(
#                 timetable__id=scheduled_obj.id
#             ).get(student=request.user.id)
#             if student_obj.status != "ALPHA":
#                 res["is_attended"] = True

#             return Response(res)
#         return Response(
#             {"error": {"status": 404, "message": "tidak ada kelas saat ini"}}
#         )

#     def post(self, request):
#         lecture = current_lecture(request.user.id, ClassroomTimetable)
#         serializer = StudentPresenceSer(data=request.data)
#         if lecture:
#             if serializer.is_valid():
#                 timetable_id = lecture.id
#                 student_id = request.user.id
#                 # lat = request.data["lat"]
#                 # lng = request.data["lng"]
#                 token = request.data["token"]
#                 # Check Token
#                 if token == lecture.token:
#                     # Check Coordinate
#                     if True:  # validation(lat=lat, lng=lng):
#                         time = auto_now("time")
#                         student_obj = (
#                             ClassroomAttendance.objects.filter(timetable=timetable_id)
#                             .filter(
#                                 timetable__start_time__lte=time,
#                                 timetable__end_time__gte=time,
#                             )
#                             .get(student=student_id)
#                         )
#                         if student_obj.status == "ALPHA":
#                             student_obj.status = "HADIR"
#                             student_obj.save()
#                             return Response(
#                                 {
#                                     "success": {
#                                         "status": 200,
#                                         "message": "Anda Berhasil Absen",
#                                     }
#                                 },
#                                 status=status.HTTP_200_OK,
#                             )
#                         return Response(
#                             {"error": {"status": 409, "message": "Anda sudah absen"}},
#                             status=status.HTTP_409_CONFLICT,
#                         )
#                     return Response(
#                         {
#                             "error": {
#                                 "status": 403,
#                                 "message": "Anda diluar titik point",
#                             }
#                         },
#                         status=status.HTTP_403_FORBIDDEN,
#                     )
#                 return Response(
#                     {"error": {"status": 403, "message": "Token anda salah"}},
#                     status=status.HTTP_403_FORBIDDEN,
#                 )
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         return Response(
#             {"error": {"status": 401, "message": "Tidak ada kelaas"}},
#             status=status.HTTP_401_UNAUTHORIZED,
#         )
