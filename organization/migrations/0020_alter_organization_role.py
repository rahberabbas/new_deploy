# Generated by Django 4.1.6 on 2023-05-26 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0019_alter_organization_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='role',
            field=models.CharField(blank=True, choices=[('Collaborator', 'Collaborator'), ('Hiring Manager', 'Hiring Manager'), ('Recruiter', 'Recruiter')], max_length=255, null=True),
        ),
    ]
