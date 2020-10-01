#Core Django Dependencies
from django.db import models
from django.db.models.signals import post_save,post_delete
from django.core.exceptions import ValidationError 
from  admins.models import Admin,BasicInfo,School
from teachers.models import Teacher,Class
from django.utils.timezone import localdate
from parents.models import Parent
from datetime import date as Date
from tools import years_ago
class Term(models.Model):
	FIRST_TERM = "1st Term"
	SECOND_TERM = "2nd Term"
	THIRD_TERM = "3rd Term"
	term_choices = (
	(FIRST_TERM,FIRST_TERM),
	(SECOND_TERM,SECOND_TERM),
	(THIRD_TERM,THIRD_TERM),
	)
	school = models.ForeignKey(School,on_delete=models.CASCADE) 
	term = models.CharField(max_length=20,choices = term_choices)
	year = models.SmallIntegerField()
	current_session = models.BooleanField(default=False)
	
	@property
	def session(self):		
		return f"{self.year}/{self.year+1}"
	def __str__(self):
		return f"{self.session} Session : {self.term}"
	def set_as_current(self):
		terms = Term.objects.filter(school=self.school).exclude(pk=self.pk)
		terms.update(current_session=False)
		self.current_session = True
		self.save()
	def save(self,*args,**kwargs):
		#Check if current_session already exists and raise error
		if self.current_session:
			if Term.objects.filter(school=self.school,current_session=True).exclude(pk=self.pk).exists():
				raise ValidationError("A current session already exists, call set_as_current method to set it as current session")
		super(Term,self).save(*args,**kwargs)


	class Meta:
		ordering = ["-year","-term"]
		constraints = [models.UniqueConstraint(fields=["term","year","school"],name="unique_term"),]

	
# Create your models here.
class Student(models.Model):
	sex_choices=(('male','male'),
		('female','female')
	)
	
	name = models.CharField(max_length=100)
	parents = models.ManyToManyField(Parent)
	student_email = models.EmailField(blank=True,null=True)
	phone_no= models.CharField(max_length=100,blank=True,null =True)
	Class = models.ForeignKey(Class,on_delete=models.SET_NULL,null=True)
	photo = models.ImageField(default='default.jpg', upload_to = 'Student_Pictures')
	address = models.CharField(max_length=100,null=True)
	date_of_birth=models.DateField(null=True)
	sex =models.CharField(max_length=10, choices= sex_choices,null=True)
	state_of_origin = models.CharField(max_length=30,null=True)
	created_at = models.DateField(auto_now_add=True)
	update_at = models.DateField(auto_now=True)
	
	@property
	def age(self):
		try:
			result = years_ago(self.date_of_birth)
			return result
		except:
			return "Not available"
	def __str__(self):
		return self.name
	class Meta:
		ordering = ["name",]

def get_default_term():
	if Term.objects.first():
		return Term.objects.first().pk
	else:
		return Term.objects.create(term="1st Term",year=date.today().year).pk

class Performance(models.Model):
	comment_choices = (('excellent','excellent'),
	('good','good'),
	('average','average'),
	('fair','fair'),('poor','poor')
	)
	subject = models.CharField(max_length=40)
	student=models.ForeignKey(Student, on_delete=models.CASCADE )
	Class = models.ForeignKey(Class,on_delete=models.CASCADE)
	term = models.ForeignKey(Term,on_delete=models.CASCADE)
	test = models.FloatField()
	exam = models.FloatField()
	comment = models.CharField(max_length=30, choices= comment_choices)
	created_at = models.DateTimeField(auto_now_add=True)
	update_at = models.DateTimeField(auto_now=True)
	
	def __str__(self):
		return self.subject + " : " + str(self.total)
	@property
	def total(self):
		return self.test + self.exam
	class Meta:
		ordering = ["subject"]
		constraints = [models.UniqueConstraint(fields=["term","subject","student"],name="unique_performance"),]

	
def prevent_future_dates(date):
	if date > localdate():
		print("ValidationError should be raised")
		raise ValidationError("Future dates cannot be added")


class Attendance(models.Model):
	Class = models.ForeignKey(Class,on_delete=models.CASCADE,unique_for_date="date")
	present_students=models.ManyToManyField(Student, related_name='attendance')
	date = models.DateField(validators=[prevent_future_dates])
	def __str__(self):
		return  'Students present on '+ str(self.date) + ", Class : " + self.Class.class_name
		
	class Meta:
		ordering = ["-date"]
		constraints = [models.UniqueConstraint(fields=["Class","date"],name="unique_attendance")]



class School_activity_log(models.Model):
	Class = models.ForeignKey(Class,on_delete=models.CASCADE)
	Activity_type = models.CharField(max_length=250)
	Activity_date_and_time = models.DateTimeField(auto_now=True)
	Activity_info = models.CharField(max_length=500)
	viewed = models.BooleanField(default=False)
	def __str__(self):
		return f"{self.Activity_type} : {self.Activity_info} at {self.Activity_date_and_time}."
		
	class Meta:
		ordering = ["-Activity_date_and_time"]
		
		
