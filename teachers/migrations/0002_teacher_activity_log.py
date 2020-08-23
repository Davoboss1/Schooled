# Generated by Django 3.0.3 on 2020-03-30 12:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Teacher_activity_log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Activity_type', models.CharField(max_length=250)),
                ('Activity_date_and_time', models.DateTimeField(auto_now=True)),
                ('Activity_info', models.CharField(max_length=500)),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teachers.Teacher')),
            ],
            options={
                'ordering': ['-Activity_date_and_time'],
            },
        ),
    ]
