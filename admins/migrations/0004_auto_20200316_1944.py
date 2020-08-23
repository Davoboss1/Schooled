# Generated by Django 3.0.3 on 2020-03-16 18:44

import admins.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admins', '0003_auto_20200316_1751'),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender', models.CharField(max_length=30, validators=[admins.models.username_exists])),
                ('reciever', models.CharField(max_length=30, validators=[admins.models.username_exists])),
                ('subject', models.CharField(max_length=100)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='messages',
            name='is_reply',
        ),
        migrations.RemoveField(
            model_name='messages',
            name='reciever',
        ),
        migrations.RemoveField(
            model_name='messages',
            name='sender',
        ),
        migrations.RemoveField(
            model_name='messages',
            name='subject',
        ),
        migrations.AddField(
            model_name='messages',
            name='conversation',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='admins.Conversation'),
            preserve_default=False,
        ),
    ]
