# Generated by Django 3.0.7 on 2020-09-11 22:22

import accounts.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender', models.CharField(max_length=30, null=True, validators=[accounts.models.username_exists])),
                ('subject', models.CharField(max_length=100)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('reciever', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='Messages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('message_datetime', models.DateTimeField(auto_now_add=True)),
                ('message_read', models.BooleanField(default=False)),
                ('sent_by', models.CharField(max_length=30, null=True, validators=[accounts.models.username_exists])),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.Conversation')),
            ],
            options={
                'ordering': ['-message_datetime'],
            },
        ),
    ]