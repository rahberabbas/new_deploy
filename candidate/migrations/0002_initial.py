# Generated by Django 4.1.6 on 2023-05-08 05:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('job', '0001_initial'),
        ('candidate', '0001_initial'),
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='skill',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='job.job'),
        ),
        migrations.AddField(
            model_name='skill',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candidate.candidate'),
        ),
        migrations.AddField(
            model_name='resume',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='job.job'),
        ),
        migrations.AddField(
            model_name='resume',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candidate.candidate'),
        ),
        migrations.AddField(
            model_name='link',
            name='job',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='job.job'),
        ),
        migrations.AddField(
            model_name='link',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candidate.candidate'),
        ),
        migrations.AddField(
            model_name='certificate',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='job.job'),
        ),
        migrations.AddField(
            model_name='certificate',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candidate.candidate'),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='job.job'),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candidate.candidate'),
        ),
        migrations.AddField(
            model_name='candidateexperience',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='job.job'),
        ),
        migrations.AddField(
            model_name='candidateexperience',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candidate.candidate'),
        ),
        migrations.AddField(
            model_name='candidateeducation',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='job.job'),
        ),
        migrations.AddField(
            model_name='candidateeducation',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candidate.candidate'),
        ),
        migrations.AddField(
            model_name='candidate',
            name='organizations',
            field=models.ManyToManyField(blank=True, to='organization.organizationprofile'),
        ),
    ]