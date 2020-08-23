# Generated by Django 2.2.1 on 2020-01-14 16:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('school_name', models.CharField(max_length=100)),
                ('school_address', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('Secondary_School', 'Secondary_School'), ('Primary_School', 'Primary_School')], max_length=30)),
                ('approved', models.BooleanField()),
                ('motto', models.TextField(blank=True, null=True)),
                ('school_Anthem', models.TextField(blank=True, null=True)),
                ('vision', models.TextField(blank=True, null=True)),
                ('mission', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(default='default.jpg', upload_to='School_Pictures')),
                ('school_email', models.EmailField(max_length=254)),
                ('created_at', models.DateTimeField()),
                ('update_at', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='SchoolUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(choices=[('Admin', 'Admin'), ('Teacher', 'Teacher'), ('Parent', 'Parent')], max_length=20)),
                ('profile_picture', models.ImageField(default='default.jpg', upload_to='Profile_Pictures')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=100)),
                ('date_of_birth', models.DateField()),
                ('sex', models.CharField(choices=[('male', 'male'), ('female', 'female')], max_length=10)),
                ('state_of_origin', models.CharField(max_length=100)),
                ('state_of_residence', models.CharField(max_length=100)),
                ('religion', models.CharField(choices=[('Christianity', 'Christianity'), ('Islam', 'Islam'), ('Others', 'Others')], max_length=100)),
                ('phone_no', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('update_at', models.DateField(auto_now=True)),
                ('marital_status', models.CharField(choices=[('Single', 'Single'), ('Married', 'Married'), ('Divorced', 'Divorced'), ('Widowed', 'Widowed')], max_length=10)),
                ('school', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='admins.School')),
                ('school_user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='admins.SchoolUser')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
