from django.shortcuts import render,Http404,HttpResponse,redirect
from django.db.utils import IntegrityError
from django.contrib.auth.forms import PasswordChangeForm
from accounts.forms import UserUpdateForm
from .forms import ParentForm
from students.models import Term
from admins.views import get_errors_in_text
from tools import save_picture,view_for,require_ajax
# Create your views here.
#Parents homepage view
@view_for("parent")
def parents_homepage(request):
	term= Term.objects.first()
	#current parent
	parent = request.user.parent
	#Form to change password
	password_change_form = PasswordChangeForm(user = request.user)
	user_update_form = UserUpdateForm(instance=request.user)
	#Form to update information
	parent_form = ParentForm(instance=parent)
	
	#rendering 
	return render(request,"parents/parents_homepage.html",{"parent":parent,"password_change_form":password_change_form,"parent_form":parent_form,"user_update_form":user_update_form})
	
#update parent info
@view_for("parent")
@require_ajax
def update(request):
	#Check if request method is post
	if request.method == "POST":
		#Get type from post request
		'''
		there are three type.
		First username. For updating username and user related data.
		Second Password. for updating password and password related data.
		Third Info. for updating uset information.
			'''
		type = request.POST.get("type")
		#Get current user
		user = request.user
			
		if type == "Username":
			#try to assign all user info 
			user_update_form = UserUpdateForm(request.POST,instance=user)
			if user_update_form.is_valid():
				user = user_update_form.save()
				save_picture(user.profile_picture,request.FILES.get("profile-picture"))
				return HttpResponse("Success")
			else:
				return HttpResponse(get_errors_in_text(user_update_form))
		elif type == "Password":
			#change password form
			user_pcf = PasswordChangeForm(user,request.POST)
			if user_pcf.is_valid():
				user_pcf.save()
				return HttpResponse("Redirect")
			else:
				return HttpResponse(get_errors_in_text(user_pcf))
		#if post request is of type Info
		#this type of post request changes the user information
		elif type == "Info":
			#Change parent info
			user_info = ParentForm(request.POST,instance=user.parent)
			if user_info.is_valid():
				user_info.save()
				return HttpResponse("Success")
			else:
				return HttpResponse(get_errors_in_text(user_info))		

