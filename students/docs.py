from drf_yasg import openapi


class StudentDoc:
    student_dashboard_get = {
        "200": openapi.Response(
            description="Response GET",
            examples={
                "application/json": {
                    "greet": "string",
                    "currentLecture": {
                        "subject": "string",
                        "teacher": {
                            "first_name": "Andika",
                            "last_name": "Pratama",
                        },
                        "time": {
                            "start_time": "07:00",
                            "end_time": "10:00",
                        },
                    },
                    "currentAttendance": {
                        "work_time": "07:30",
                        "home_time": "15:00",
                        "clock_in": "07:30",
                        "clock_out": "15:00",
                    },
                    "user": {
                        "first_name": "Andika",
                        "last_name": "Pratama",
                    },
                }
            },
        ),
        "203": openapi.Response(
            description="Tidak Ada Kelas (Nullable)",
            examples={
                "application/json": {
                    "greet": "string",
                    "currentLecture": {
                        "subject": None,
                        "teacher": {
                            "first_name": None,
                            "last_name": None,
                        },
                        "time": {
                            "start_time": None,
                            "end_time": None,
                        },
                    },
                    "currentAttendance": {
                        "work_time": None,
                        "home_time": None,
                        "clock_in": None,
                        "clock_out": None,
                    },
                    "user": {
                        "first_name": "Andika",
                        "last_name": "Pratama",
                    },
                }
            },
        ),
        "403": openapi.Response(
            description="Jika User Tidak Mempunyai Role Student",
            examples={
                "aplication/json": {
                    "detail": "You do not have permission to perform this action."
                }
            },
        ),
    }
    student_history_get = {
        "200": openapi.Response(
            description="Jika ada history maka akan ditampilkan semua",
            examples={
                "application/json": {
                    "Jun 2022": [
                        {"name": "Basis Data", "date": "2022-06-28", "status": "ALPHA"},
                        {"name": "string", "date": "string", "status": "string"},
                    ],
                    "May 2022": [
                        {"name": "string", "date": "string", "status": "string"},
                    ],
                }
            },
        ),
        "203": openapi.Response(
            description="Jika tidak ada history yang ditampilkan",
            examples={"aplication/json": {}},
        ),
    }

    student_schedule_get = {
        "200": openapi.Response(
            description="Response GET",
            examples={
                "application/json": {
                    "06/28/2022": [
                        {
                            "id": 7,
                            "on_going": False,
                            "subject": "Basis Data",
                            "teacher": {
                                "first_name": "Dian Nirmala Santi",
                                "last_name": "S.Kom",
                            },
                            "start_time": "21:42:00",
                            "end_time": "21:42:00",
                        },
                        {
                            "id": 9,
                            "on_going": True,
                            "subject": "Basis Data",
                            "teacher": {
                                "first_name": "Dian Nirmala Santi",
                                "last_name": "S.Kom",
                            },
                            "start_time": "22:00:00",
                            "end_time": "23:50:00",
                        },
                    ],
                    "06/29/2022": [
                        {
                            "id": 8,
                            "on_going": False,
                            "subject": "Basis Data",
                            "teacher": {
                                "first_name": "Dian Nirmala Santi",
                                "last_name": "S.Kom",
                            },
                            "start_time": "22:02:00",
                            "end_time": "22:02:00",
                        },
                    ],
                }
            },
        ),
    }

    student_statistic_get = {
        "200": openapi.Response(
            description="",
            examples={
                "aplications/json": {
                    "leave": 0,
                    "absent": 0,
                    "sick": 0,
                    "presence": 1.0,
                    "indicator": "Aman",
                }
            },
        )
    }

    student_presence_get = {
        "200": openapi.Response(
            description="",
            examples={
                "application/json": {
                    "is_attended": False,
                    "name": "string",
                    "teacher": "string",
                    "time": "18:57 - 20:57 WIB",
                    "user": {"address": "string"},
                }
            },
        ),
        "404": openapi.Response(
            description="",
            examples={
                "aplication/json": {
                    "error": {"status": 404, "message": "tidak ada kelas saat ini"}
                }
            },
        ),
    }

    student_presence_post = {
        "200": openapi.Response(
            description="",
            examples={
                "aplication/json": {
                    "success": {
                        "status": 200,
                        "message": "Anda Berhasil Absen",
                    }
                },
            },
        ),
        "409": openapi.Response(
            description="",
            examples={
                "aplication/json": {
                    "error": {"status": 409, "message": "Anda sudah absen"}
                }
            },
        ),
        "403": openapi.Response(
            description="",
            examples={
                "aplication/json (1)": {
                    "error": {
                        "status": 403,
                        "message": "Anda diluar titik point",
                    }
                },
                "aplication/json (2)": {
                    "error": {"status": 403, "message": "Token anda salah"}
                },
            },
        ),
        "401": openapi.Response(
            description="Ini cuma pencegahan jika ada yang mencoba POST, karena respon ini sudah ada di GET",
            examples={
                "aplication/json": {
                    "error": {"status": 401, "message": "Tidak ada kelas"}
                }
            },
        ),
    }
