# Generated by Django 4.1.6 on 2023-05-29 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0022_alter_organization_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='role',
            field=models.CharField(blank=True, choices=[('Hiring Manager', 'Hiring Manager'), ('Recruiter', 'Recruiter'), ('Collaborator', 'Collaborator')], max_length=255, null=True),
        ),
    ]
