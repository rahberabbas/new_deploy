# Generated by Django 4.1.6 on 2023-05-25 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0013_alter_organization_role_activitylog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activitylog',
            name='activity_type',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='role',
            field=models.CharField(blank=True, choices=[('Collaborator', 'Collaborator'), ('Hiring Manager', 'Hiring Manager'), ('Recruiter', 'Recruiter')], max_length=255, null=True),
        ),
    ]
