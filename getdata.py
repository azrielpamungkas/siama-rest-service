import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django

django.setup()

from django.core.management import call_command
import pandas as pd
import datetime

from os import listdir
from os.path import isfile, join, splitext
from django.contrib.auth.models import User

users = User.objects.all()[2:]
data = {'nama': [], 'username': [], 'role': [], 'kelas': []}
for user in users:
    role = (lambda x: "Guru" if x == "teacher" else "Murid" if x == "student" else x if x == "staff" else x)((lambda x: None if x == None else x.name)(user.groups.all().first()))
    name = user.first_name
    username = user.username
    kelas = (lambda x: None if x == None else x.grade)(user.kelasku.all().first())
    data['nama'].append(name)
    data['username'].append(username)
    data['role'].append(role)
    data['kelas'].append(kelas)

df = pd.DataFrame(data)
df.to_csv('users.csv', index=False)

