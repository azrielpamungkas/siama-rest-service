# Generated by Django 3.2.13 on 2022-09-12 03:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classrooms', '0009_alter_classroomtimetable_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='classroomsubject',
            name='slug',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
    ]