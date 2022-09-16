import datetime


def auto_now(promt="default"):
    if promt == "default":
        return datetime.datetime.now()
    elif promt == "time":
        return datetime.datetime.now().time()
    elif promt == "today":
        return datetime.date.today()


def current_lecture(user, model):
    try:
        current_lecture = (
            model.objects.all()
            .filter(date=datetime.date.today())
            .filter(start_time__lte=datetime.datetime.now().time())
            .filter(end_time__gt=datetime.datetime.now().time())
            .get(subject__classroom__student=user)
        )
        return current_lecture
    except:
        return None


def current_lecture_teacher(user, model):
    # masih sering bug disini kalau ada banyak jadwal
    try:
        current_lecture = (
            model.objects.all()
            .filter(date=datetime.date.today())
            .filter(start_time__lte=datetime.datetime.now().time())
            .filter(end_time__gt=datetime.datetime.now().time())
            .get(subject__teacher=user)
        )
        return current_lecture
    except:
        return None
