from drf_yasg import openapi


class AttendanceDoc:
    attendance_get = {
        "200": openapi.Response(
            description="Response GET",
            examples={
                "application/json": {
                    "attendance_type": "MRD",
                    "attendance_status": "Clock-Out",
                    "date": "2022-06-30",
                    "work_time": "08:51:00",
                    "home_time": "15:51:00",
                    "clock_in": "9:46",
                    "clock_out": None,
                    "user": {"address": "Soul Buoy"},
                }
            },
        ),
        "404": openapi.Response(
            description="",
            examples={
                "aplication/json": {
                    "message": {
                        "status": "info",
                        "detail": "tidak ada jadwal untuk hari ini",
                    }
                }
            },
        ),
    }

    attendance_post = {
        "200": openapi.Response(
            description="Response GET",
            examples={
                "application/json (success clock out)": {
                    "status": 200,
                    "clock_out": "07:00",
                    "next_attendance_status": "Done!",
                    "message": "anda berhasil clock out",
                },
                "application/json (success clock out)": {
                    "status": 200,
                    "clock_in": "07:00",
                    "next_attendance_status": "Clock-In",
                    "message": "anda berhasil clock in",
                },
            },
        ),
        "409": openapi.Response(
            description="",
            examples={
                "error": "invalid_post",
                "error_description": "Anda sudah absen untuk saat ini",
            },
        ),
    }
