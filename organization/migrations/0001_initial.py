# Generated by Django 4.1.6 on 2023-05-08 05:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizationPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=265, null=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='SuperAdmin',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='superadmin', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('srefid', models.SlugField(blank=True, null=True)),
                ('company_name', models.CharField(blank=True, max_length=256, null=True)),
                ('name', models.CharField(blank=True, max_length=256, null=True)),
                ('paddress', models.CharField(blank=True, max_length=256, null=True)),
                ('verified', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'SuperAdmin Account',
                'verbose_name_plural': 'SuperAdmins Account',
            },
            bases=('accounts.user',),
        ),
        migrations.CreateModel(
            name='OrganizationProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_id', models.SlugField(blank=True, null=True, unique=True)),
                ('about_org', models.TextField(blank=True, null=True)),
                ('about_founder', models.TextField(blank=True, null=True)),
                ('org_Url', models.CharField(blank=True, max_length=256, null=True)),
                ('contact_Number', models.CharField(blank=True, max_length=256, null=True)),
                ('company_Size', models.CharField(blank=True, max_length=256, null=True)),
                ('workplace_Type', models.CharField(blank=True, max_length=256, null=True)),
                ('headquarter_Location', models.TextField(blank=True, null=True)),
                ('branch_Office', models.TextField(blank=True, null=True)),
                ('organization_Benefits', models.TextField(blank=True, null=True)),
                ('funding_Details', models.TextField(blank=True, null=True)),
                ('logo', models.FileField(default='default_image.jpeg', upload_to='org/profile/logo/')),
                ('banner', models.FileField(default='default_image.jpeg', upload_to='org/profile/banner/')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='organization.superadmin')),
            ],
            options={
                'verbose_name': 'Organization Profile',
                'verbose_name_plural': 'Organization Profiles ',
            },
        ),
        migrations.CreateModel(
            name='OrganizationMailIntegration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('access_token', models.CharField(blank=True, max_length=1000)),
                ('refresh_token', models.CharField(blank=True, max_length=1000)),
                ('expires_in', models.IntegerField()),
                ('is_expired', models.BooleanField(default=False)),
                ('provider', models.CharField(blank=True, max_length=255)),
                ('scope', models.CharField(max_length=256)),
                ('label_id', models.CharField(max_length=120)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organization.organizationprofile', to_field='unique_id')),
            ],
            options={
                'verbose_name': 'Organization Mail Integration',
                'verbose_name_plural': 'Organization Mail Integrations',
            },
        ),
        migrations.CreateModel(
            name='OrganizationGallery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.FileField(blank=True, null=True, upload_to='org/gallery')),
                ('organizationProfile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organization.organizationprofile')),
            ],
            options={
                'verbose_name': 'Organization Gallery',
                'verbose_name_plural': 'Organization Galleries ',
            },
        ),
        migrations.CreateModel(
            name='OrganizationFounder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.FileField(blank=True, null=True, upload_to='org/founder')),
                ('name', models.CharField(blank=True, max_length=256, null=True)),
                ('designation', models.CharField(blank=True, max_length=256, null=True)),
                ('organizationProfile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organization.organizationprofile')),
            ],
            options={
                'verbose_name': 'Organization Founder',
                'verbose_name_plural': 'Organization Founders ',
            },
        ),
        migrations.CreateModel(
            name='OrganizationCalendarIntegration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('access_token', models.CharField(blank=True, max_length=1000)),
                ('refresh_token', models.CharField(blank=True, max_length=1000)),
                ('expires_in', models.IntegerField()),
                ('is_expired', models.BooleanField(default=False)),
                ('provider', models.CharField(blank=True, max_length=255)),
                ('scope', models.CharField(max_length=256)),
                ('calendar_id', models.CharField(blank=True, max_length=1000)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organization.organizationprofile', to_field='unique_id')),
            ],
            options={
                'verbose_name': 'Organization Calendar Integration',
                'verbose_name_plural': 'Organization Calendar Integrations',
            },
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='organization', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('orefid', models.SlugField(blank=True, null=True)),
                ('name', models.CharField(blank=True, max_length=256, null=True)),
                ('verified', models.BooleanField(default=False)),
                ('role', models.CharField(blank=True, choices=[('Collaborator', 'Collaborator'), ('Hiring Manager', 'Hiring Manager'), ('Recruiter', 'Recruiter')], max_length=255, null=True)),
                ('dept', models.CharField(blank=True, max_length=255, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.superadmin')),
                ('organization_permissions', models.ManyToManyField(blank=True, to='organization.organizationpermission')),
            ],
            options={
                'verbose_name': 'Organization Account',
                'verbose_name_plural': 'Organizations Account',
            },
            bases=('accounts.user',),
        ),
        migrations.CreateModel(
            name='IndividualProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_id', models.SlugField(blank=True, null=True)),
                ('profile', models.FileField(default='default_image.jpeg', upload_to='org/profile/')),
                ('organization_Name', models.CharField(blank=True, max_length=256, null=True)),
                ('full_Name', models.CharField(blank=True, max_length=256, null=True)),
                ('contact_Number', models.CharField(blank=True, max_length=256, null=True)),
                ('email', models.CharField(blank=True, max_length=256, null=True)),
                ('title', models.CharField(blank=True, max_length=256, null=True)),
                ('department', models.CharField(blank=True, max_length=256, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Individual Profile',
                'verbose_name_plural': 'Individual Profiles ',
            },
        ),
        migrations.CreateModel(
            name='IndividualLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=1000, null=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('individualProfile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organization.individualprofile')),
            ],
            options={
                'verbose_name': 'Individual Social Link',
                'verbose_name_plural': 'Individual Social Links',
                'ordering': ('timestamp',),
            },
        ),
    ]
