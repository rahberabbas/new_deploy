# Generated by Django 4.1.6 on 2023-05-26 07:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0002_notification'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='arefid',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='job_name',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='refid',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='team',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='team_name',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='user_name',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='vendor',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='vendor_name',
        ),
    ]