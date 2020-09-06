import os
from datetime import date as Date
from django.db.models.signals import post_save,pre_save,post_delete
from .models import Student,School_activity_log,Performance,Attendance


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
		school_log_obj.Activity_info= f"{instance.Class.class_name} Attendance for {date} has been marked."
	else:
		school_log_obj.Activity_info= f"{instance.Class.class_name} Marked attendance for {date} has been updated."
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
	
def student_post_delete(sender,instance,**kwargs):
	photo = instance.photo
	if photo.name != "default.jpg":
		os.remove(photo.path)

post_save.connect(attendance_log,sender=Attendance)
post_save.connect(performance_log,sender=Performance)
post_save.connect(student_log,sender=Student)
post_delete.connect(delete_student_log,sender=Student)
post_delete.connect(student_post_delete,sender=Student)
