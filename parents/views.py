from django.shortcuts import render,Http404,HttpResponse,redirect
from django.db.utils import IntegrityError
from django.contrib.auth.forms import UserChangeForm,PasswordChangeForm
from .forms import ParentForm
from students.models import Term

# Create your views here.
#Parents homepage view
def parents_homepage(request):
	term= Term.objects.first()
	#current parent
	parent = request.user.schooluser.parent
	#Form to change password
	password_change_form = PasswordChangeForm(user = request.user)
	#Form to update information
	parent_form = ParentForm(instance=parent)
	
	#rendering 
	return render(request,"parents/parents_homepage.html",{"parent":parent,"password_change_form":password_change_form,"parent_form":parent_form})
	
#update parent info
def update(request):
	#Check if request is ajax
	if request.is_ajax():
		#Check if request method is post
		if request.method == "POST":
			print(request.POST)
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
				try:
					user.username = request.POST.get("username")
					user.first_name = request.POST.get("first_name")
					user.last_name = request.POST.get("last_name")
					user.email = request.POST.get("email")
					user.save()
					return HttpResponse("Success")
				except IntegrityError:
					return HttpResponse("<h6>Username already exists </h6>")
			elif type == "Password":
				#change password form
				user_pcf = PasswordChangeForm(user,request.POST)
				if user_pcf.is_valid():
					user_pcf.save()
					return HttpResponse("Redirect")
				else:
					
					#If form is invalid
					#create an empty string for error text in html
					error_string = str()
					#loop over error messages
					for key in user_pcf.errors.as_data().keys():
						print(user_pcf.errors.as_data()[key])
					#write the error messages in h6 tags
						error_string+=f"<hr> <h6>{user_pcf.errors.as_data()[key][0].message}</h6>"
					return HttpResponse(error_string)
			#if post request is of type Info
			#this type of post request changes the user information
			elif type == "Info":
				#Change parent info
				user_info = ParentForm(request.POST,instance=user.schooluser.parent)
				if user_info.is_valid():
					user_info.save()
					return HttpResponse("Success")
				else:
					return HttpResponse(user_info.errors.as_ul())		
			
	return Http404()
	
