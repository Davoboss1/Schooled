#Core Django Dependencies
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
	level_choices= (
		('Admin','Admin'),
		('Teacher','Teacher'),
		('Parent','Parent'),
	)
	level = models.CharField(max_length=20, choices = level_choices)
	profile_picture = models.ImageField(default='default.jpg', upload_to = 'Profile_Pictures')
	def __str__(self):
		return f"Username : {self.username} , FullName : {self.get_full_name()}"


class help(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    def __str__(self):
        return self.title
