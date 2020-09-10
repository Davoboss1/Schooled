from django.db import models
from admins.models import Admin
from django.contrib.auth import get_user_model
from teachers.models import Teacher
from admins.models import BasicInfo,School

# Create your models here.
class Parent(models.Model):
	sex_choices=(
		('male','male'),
		('female','female')
	)
	user = models.OneToOneField(get_user_model(),on_delete=models.CASCADE)
	address = models.CharField(max_length=100,null=True,blank=True)
	phone_no= models.CharField(max_length=100,null=True,blank=True)
	
	created_at = models.DateField(auto_now_add=True)
	update_at = models.DateField(auto_now=True)
	def __str__(self):
		return "Username: " + self.user.username + ", Full name: " + self.user.get_full_name()

	@property
	def full_name(self):
		return self.user.get_full_name()



