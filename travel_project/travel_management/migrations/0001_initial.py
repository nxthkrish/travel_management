# Generated by Django 5.1.6 on 2025-03-10 09:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('admin', 'Admin'), ('employee', 'Employee'), ('manager', 'Manager')], default='employee', max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(default='Employee', max_length=50)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='travel_management.customuser')),
            ],
        ),
        migrations.CreateModel(
            name='Manager',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department', models.CharField(max_length=50)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='travel_management.customuser')),
            ],
        ),
        migrations.CreateModel(
            name='TravelRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('destination', models.CharField(max_length=100)),
                ('purpose', models.TextField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected'), ('Clarification Requested', 'Clarification Requested'), ('Closed', 'Closed')], default='Pending', max_length=25)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='travel_management.employee')),
            ],
        ),
        migrations.CreateModel(
            name='Approval',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approved', models.BooleanField(null=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('manager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='travel_management.manager')),
                ('travel_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='travel_management.travelrequest')),
            ],
        ),
        migrations.CreateModel(
            name='AdminRequestProcessing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clarification_needed', models.BooleanField(default=False)),
                ('closed', models.BooleanField(default=False)),
                ('admin', models.ForeignKey(limit_choices_to={'role': 'admin'}, on_delete=django.db.models.deletion.CASCADE, to='travel_management.customuser')),
                ('travel_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='travel_management.travelrequest')),
            ],
        ),
    ]
