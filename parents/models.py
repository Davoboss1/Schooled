from django.db import models
from admins.models import Admin,SchoolUser
from teachers.models import Teacher
from admins.models import BasicInfo,School

# Create your models here.
class Parent(models.Model):
	sex_choices=(
		('male','male'),
		('female','female')
	)
	school_user = models.OneToOneField(SchoolUser,on_delete=models.CASCADE)
	address = models.CharField(max_length=100,null=True,blank=True)
	date_of_birth=models.DateField(null=True,blank=True)
	sex = models.CharField(max_length=10, choices=sex_choices,null=True,blank=True)
	state_of_origin = models.CharField(max_length=100,null=True,blank=True)
	phone_no= models.CharField(max_length=100,null=True,blank=True)
	
	created_at = models.DateField(auto_now_add=True)
	update_at = models.DateField(auto_now=True)
	@property
	def age(self):
		result = self.date.today().year - self.date_of_birth.year
		return result
	def __str__(self):
		return self.full_name
	@property
	def full_name(self):
		return self.school_user.user.get_full_name()
		
