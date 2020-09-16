from datetime import date as Date
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from tools import years_ago


#Create your models here
#Abstract model for every profile info
class BasicInfo(models.Model):
	address = models.CharField(max_length=100,null=True)
	phone_no= models.CharField(max_length=100, null =True)
	created_at = models.DateField(auto_now_add=True)
	update_at = models.DateField(auto_now=True)
	class Meta:
		abstract = True

#Model for every School Adminstrator
class Admin(BasicInfo):
	user = models.OneToOneField(get_user_model(),on_delete=models.CASCADE)
	def __str__(self):
		return self.user.get_full_name()
	@property
	def full_name(self):
		return self.user.get_full_name()
		
#School model
class School(models.Model):
	type_choices=(
		('Secondary School','Secondary School'),
		('Primary School','Primary School'),
		('Others','Others')
	)
	admin = models.ForeignKey(Admin,on_delete=models.CASCADE,related_name="schools")
	school_name =models.CharField(max_length=100,unique=True)
	school_address =models.CharField(max_length=100)
	type = models.CharField(max_length=30, choices = type_choices)
	
	approved = models.BooleanField()
	motto = models.TextField(blank = True, null = True)
	image= models.ImageField(default='default.jpg', upload_to = 'School_Pictures')
	school_email = models.EmailField()
	created_at = models.DateTimeField(auto_now_add=True)
	update_at = models.DateTimeField(auto_now=True)
	
	def __str__(self):
		return self.school_name
		
		
