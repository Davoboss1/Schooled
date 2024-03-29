from django.db import models
from django.contrib.auth import get_user_model
from admins.models import Admin,School
from admins.models import BasicInfo
from django.db.models.signals import post_delete,pre_delete
# Create your models here.

class Teacher(BasicInfo):
    user = models.OneToOneField(get_user_model(),on_delete=models.CASCADE)
    def __str__(self):
        return "Username: " + self.user.username + ", Full name: " + self.user.get_full_name()

    @property
    def full_name(self):
        return self.user.get_full_name()
		
class Class(models.Model):
	school = models.ForeignKey(School,models.CASCADE)
	class_name = models.CharField(max_length=20)
	teacher = models.OneToOneField(Teacher,on_delete=models.SET_NULL,null=True,related_name="teacher_class")
	def __str__(self):
		return str(self.class_name) + " : " + str(self.teacher)
	class Meta:
		constraints = [models.UniqueConstraint(fields=["class_name","school"],name="unique_class"),]


def delete_students(**kwargs):
	instance = kwargs['instance']
	students = instance.student_set.all()
	students.delete()

#Delete teacher and teacher user if class is deleted
def delete_teachers(**kwargs):
	try:
		instance = kwargs['instance']
		instance.teacher.user.delete()
	except:
		pass

pre_delete.connect(delete_students,sender=Class)
post_delete.connect(delete_teachers,sender=Class)
