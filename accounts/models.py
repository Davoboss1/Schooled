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


#username validator
def username_exists(value):
	print(User.objects.all())
	if not User.objects.filter(username=value).exists():
		raise ValidationError(f"{value} username does not exists")

class Conversation(models.Model):
	sender = models.CharField(max_length=30,validators=[username_exists],null=True)
	reciever = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
	subject = models.CharField(max_length=100)
	updated_at = models.DateTimeField(auto_now=True)
	def __str__(self):
		return f"Subject : {self.subject} ,From {self.sender} ,To {self.reciever} at {self.updated_at}"
	class Meta:
		ordering = ["-updated_at"]


class Messages(models.Model):
	conversation = models.ForeignKey(Conversation,on_delete=models.CASCADE)
	message = models.TextField()
	message_datetime = models.DateTimeField(auto_now_add=True)
	message_read = models.BooleanField(default=False)
	sent_by = models.CharField(max_length=30,validators=[username_exists],null=True)
	def __str__(self):
		return f"{self.conversation} Message : {self.message}"
	class Meta:
		ordering = ["-message_datetime"]

