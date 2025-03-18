# Generated by Django 5.1.6 on 2025-03-11 12:28

import django.contrib.auth.models
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('travel_management', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),
        migrations.AlterModelManagers(
            name='customuser',
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='user',
        ),
        migrations.AddField(
            model_name='customuser',
            name='date_joined',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='email address'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='first name'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_staff',
            field=models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_superuser',
            field=models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='last_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='last name'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$870000$spwBHeyme5CJLydkBEelkV$su5MD/St18UMOhwFTLmqnaEMVecYXKim+hMbzQnndXM=', max_length=128),
        ),
        migrations.AddField(
            model_name='customuser',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='username',
            field=models.CharField(default='default_username', max_length=150, unique=True),
        ),
        migrations.AddField(
            model_name='travelrequest',
            name='additional_requests',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='travelrequest',
            name='detail_message',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='travelrequest',
            name='from_location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='travelrequest',
            name='lodging_location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='travelrequest',
            name='lodging_required',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='travelrequest',
            name='requested_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='requested_travel_changes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='travelrequest',
            name='resubmitted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='travelrequest',
            name='status_updated_by',
            field=models.CharField(blank=True, choices=[('Employee', 'Employee'), ('Manager', 'Manager'), ('Admin', 'Admin')], max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='travelrequest',
            name='to_location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='travelrequest',
            name='travel_mode',
            field=models.CharField(blank=True, choices=[('Flight', 'Flight'), ('Train', 'Train'), ('Bus', 'Bus'), ('Car', 'Car')], max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='adminrequestprocessing',
            name='admin',
            field=models.ForeignKey(limit_choices_to={'role': 'admin'}, on_delete=django.db.models.deletion.CASCADE, related_name='processed_requests', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='adminrequestprocessing',
            name='travel_request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='admin_processings', to='travel_management.travelrequest'),
        ),
        migrations.AlterField(
            model_name='approval',
            name='manager',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='approved_requests', to='travel_management.manager'),
        ),
        migrations.AlterField(
            model_name='approval',
            name='travel_request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='approvals', to='travel_management.travelrequest'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='employee_profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='manager',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='manager_profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='travelrequest',
            name='destination',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='travelrequest',
            name='employee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='travel_requests', to=settings.AUTH_USER_MODEL),
        ),
    ]
