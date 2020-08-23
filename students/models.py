#Core Django Dependencies
from django.db import models
from django.db.models.signals import post_save,post_delete
from django.core.exceptions import ValidationError 
from  admins.models import Admin,BasicInfo,School
from teachers.models import Teacher,Class
from django.utils.timezone import localdate
from parents.models import Parent
from datetime import date as Date
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
	
	@property
	def session(self):		
		return f"{self.year}/{self.year+1}"
	def __str__(self):
		return f"{self.session} Session : {self.term}"
	def save(self,*args,**kwargs):
		self.year = int(self.year)
		if Term.objects.filter(school=self.school).exists():
			current_term = Term.objects.filter(school=self.school).first()
			if current_term.term == self.FIRST_TERM:
				if self.term != self.SECOND_TERM:
					raise ValidationError("Invalid value for next term")
			elif current_term.term == self.SECOND_TERM:
				if self.term != self.THIRD_TERM:
					raise ValidationError("Invalid value for next term")
			elif current_term.term == self.THIRD_TERM:
				if self.term != self.FIRST_TERM:
					raise ValidationError("Invalid value for next term")
			if current_term.year != self.year:
				if not Term.objects.filter(year=current_term.year,term=self.THIRD_TERM).exists():
					raise ValidationError("Invalid value for next term")

		super(Term,self).save(*args,**kwargs)


	class Meta:
		ordering = ["-year","-term"]
		constraints = [models.UniqueConstraint(fields=["term","year","school"],name="unique_term"),models.CheckConstraint(check=models.Q(year__gte=Date.today().year),name="previous_year")]

	
# Create your models here.
class Student(BasicInfo):
	sex_choices=(('male','male'),
		('female','female')
	)
	name = models.CharField(max_length=100)
	parents = models.ManyToManyField(Parent)
	email = models.EmailField()
	Class = models.ForeignKey(Class,on_delete=models.SET_NULL,null=True)
	photo = models.ImageField(default='default.jpg', upload_to = 'Student_Pictures')
	def __str__(self):
		return self.name
	def is_present(self,date):
		current_object = Attendance.objects.get(pk=date)
		if self in current_object.present_students.all():
			return True
		else:
			return False
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
	subject = models.CharField(max_length=40, help_text="Your Surname First")
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
		ordering = ["student"]
		constraints = [models.UniqueConstraint(fields=["term","subject","student"],name="unique_performance"),]

	
def prevent_future_dates(date):
	if date > Date.today():
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
		
		
#Signal functions
def attendance_log(**kwargs):
	instance = kwargs["instance"]
	created = kwargs["created"]
	school_log_obj = School_activity_log(Class=instance.Class,Activity_type="Attendance")
	if isinstance(instance.date,str):
		date_obj = Date.fromisoformat(instance.date)
	else:
		date_obj = instance.date
	day = str(date_obj.day)
	if day == "1":
		day += "st"
	elif day == "2":
		day += "nd"
	elif day == "3":
		day +="rd"
	else:
		day += "th"
	date = date_obj.strftime(f"%A, {day} of %B, %Y")
	if created:
		school_log_obj.Activity_info= f"{instance.Class.class_name} Attendance has been marked."
	else:
		school_log_obj.Activity_info= f"{instance.Class.class_name} Marked attendance has been updated."
	school_log_obj.save()
def performance_log(**kwargs):
	instance = kwargs["instance"]
	created = kwargs["created"]
	log_obj = School_activity_log(Class=instance.Class,Activity_type="Performance")
	if created:
		log_obj.Activity_info= f"{instance.student.name} Performance in {instance.subject} added."
	else:
		log_obj.Activity_info= f"{instance.student.name} Performance in {instance.subject} updated."
	log_obj.save()
def student_log(**kwargs):
	instance = kwargs["instance"]
	created = kwargs["created"]
	school_log_obj = School_activity_log(Class=instance.Class,Activity_type="Student")
	if created:
		school_log_obj.Activity_info= f"New student {instance.name} in {instance.Class.class_name} profile was created."
	else:
		school_log_obj.Activity_info= f"Student {instance.name} in {instance.Class.class_name} profile was updated."
	school_log_obj.save()
	
def delete_student_log(**kwargs):
	instance = kwargs["instance"]
	school_log_obj = School_activity_log(Class=instance.Class,Activity_type="Student")
	school_log_obj.Activity_info= f"Student {instance.name} in {instance.Class.class_name} profile was deleted."
	school_log_obj.save()
	
post_save.connect(attendance_log,sender=Attendance)
post_save.connect(performance_log,sender=Performance)
post_save.connect(student_log,sender=Student)
post_delete.connect(delete_student_log,sender=Student)
