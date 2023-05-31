# Generated by Django 4.1.6 on 2023-05-08 05:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionPlans',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='djstripe.customer')),
                ('organisation', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.superadmin')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='djstripe.subscription')),
            ],
        ),
    ]
