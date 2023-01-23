from django.shortcuts import render,HttpResponse,Http404,reverse,redirect
from django.http.response import HttpResponseServerError
from django.contrib.auth.forms import PasswordChangeForm
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.db.models import Q
from accounts.forms import UserCreationForm,UserUpdateForm
from .forms import TeacherForm
from .models import Class,Teacher
from students.models import School_activity_log
from accounts.models import Messages
from admins.views import get_errors_in_text
from tools import view_for,save_picture,require_ajax,get_errors_in_text, render_alert
# Create your views here.
#View for teacher homepage
@view_for("teacher")
def teacher_homepage(request):
	user = request.user
	teacher = user.teacher
	school = teacher.teacher_class.school
	#Counts teacher unread messages
	unread_msg_count = Messages.objects.filter(Q(conversation__reciever=user) | Q(conversation__sender=user.get_username()),message_read=False).exclude(sent_by=user.get_username()).count()
	#Teacher activity logs
	activity_logs = School_activity_log.objects.filter(Class=teacher.teacher_class)
	return render(request, 'teachers/teacher_homepage.html',{"user":user,"unread_msg_count":unread_msg_count,"activity_logs":activity_logs,"school":school})
	
#Admin uses this view to create teacher
@view_for("Admin")
@require_POST
def teacher_create(request):
	userform = UserCreationForm(request.POST)
	if userform.is_valid():
		admin = request.user.admin
		school = admin.schools.get(pk=request.POST.get("sch_pk"))
		teacher_class = Class.objects.get_or_create(school=school,class_name=request.POST.get("class"))[0]
		if teacher_class.teacher is None:
			user = userform.save(commit=False)
			user.level ="Teacher"
			user.save()
			teacher = Teacher.objects.create(user = user)
			teacher_class.teacher = teacher
			teacher_class.save()
		else:
			return HttpResponseServerError("Class already exists with a valid teacher.")
		
		return HttpResponse(render_alert("Teacher has been sucessfully created"))
	else:
		#If form is invalid return errors as json		
		return HttpResponseServerError(get_errors_in_text(userform))

		

@view_for("Admin")
@require_POST
#View for updating class name
def update_class(request):
	print(request.POST)
	admin = request.user.admin
	class_pk = request.POST.get("class_pk")
	class_name = request.POST.get("class_name")
	class_set = Class.objects.filter(school__admin=admin,pk=class_pk)
	if class_set.exists():
		class_set.update(class_name=class_name)
		return HttpResponse("Success")
	else:
		return HttpResponseServerError("ERROR")


#teacher uses this view to update his/her profile		
@view_for("teacher")
def update_profile(request):
		teacher = request.user.teacher
		if request.method == "POST":
			user = request.user
			if "old_password" in request.POST.keys():
				#To change user password
				user_pcf = PasswordChangeForm(user,request.POST)
				if user_pcf.is_valid():
					user_pcf.save()
					return HttpResponse("REDIRECT")
				else:
					#If form is invalid
					#create an empty string for error text in html
					error_string = str()
					#loop over error messages
					errors = user_pcf.errors.as_data()
					for key in errors.keys():
						error = errors[key]
						error = error[0].message
					#write the error messages in h6 tags
						error_string+=f"<hr> <h6>{error}</h6>"
					return HttpResponse(error_string)
			else:
				#To update teacher information
				try:
					user_update_form = UserUpdateForm(request.POST,instance=user)
					teacher_info = TeacherForm(request.POST,instance=teacher)
					if user_update_form.is_valid() and teacher_info.is_valid():
						user = user_update_form.save()
						save_picture(user.profile_picture,request.FILES.get("profile-picture"))
						teacher_info.save()
						return HttpResponse("Success")
					else:
						return HttpResponse(get_errors_in_text(user_update_form)+get_errors_in_text(teacher_info))
				except:
					return HttpResponseServerError("Failed")
		else:
			#Form to change user information
			user_update_form = UserUpdateForm(instance=request.user)
			#Form to change password
			password_change_form = PasswordChangeForm(user = request.user)
			#Form to update information
			teacher_form = TeacherForm(instance=teacher)
			return render(request,"teachers/update_profile.html",{"password_change_form":password_change_form,"teacher_form":teacher_form,"user_update_form":user_update_form})
		
#Admin uses this view to delete teacher
@view_for("admin")
@require_POST
def teacher_delete(request):
	id = int(request.POST.get("pk"))
	Teacher.objects.get(pk=id).user.delete()
	return HttpResponse("Teacher deleted Successfully")