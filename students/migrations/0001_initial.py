# Generated by Django 2.2.1 on 2020-01-14 16:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('teachers', '0001_initial'),
        ('admins', '0001_initial'),
        ('parents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Term',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('term', models.CharField(choices=[('1st Term', '1st Term'), ('2nd Term', '2nd Term'), ('3rd Term', '2nd Term')], max_length=20)),
                ('year', models.SmallIntegerField()),
            ],
            options={
                'ordering': ['-year'],
            },
        ),
        migrations.CreateModel(
            name='Student',
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
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('photo', models.ImageField(default='default.jpg', upload_to='Student_Pictures')),
                ('Class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teachers.Class')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parents.Parent')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admins.School')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Performance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(help_text='Your Surname First', max_length=40)),
                ('test', models.FloatField()),
                ('exam', models.FloatField()),
                ('total', models.FloatField()),
                ('comment', models.CharField(choices=[('excellent', 'excellent'), ('good', 'good'), ('average', 'average'), ('fair', 'fair'), ('poor', 'poor')], max_length=30)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('Class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teachers.Class')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='students.Student')),
                ('term', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='students.Term')),
            ],
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('Class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teachers.Class', unique_for_date='date')),
                ('present_students', models.ManyToManyField(related_name='attendance', to='students.Student')),
                ('term', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='students.Term')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
    ]
