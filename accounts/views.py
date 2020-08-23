import random
from datetime import datetime,timedelta
from django.shortcuts import render, redirect,HttpResponse
from django.http.response import HttpResponseNotAllowed,HttpResponseServerError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,SetPasswordForm
from django.core.mail import send_mail,BadHeaderError
from django.contrib.auth.views import LoginView
from django.template import Template,RequestContext
from admins.models import SchoolUser
from admins.forms import AdminForm,SchoolForm
from django.contrib import messages
from tools import get_expirable_session,set_expirable_session
# Create your views here.

#main homepage
#redirects authenticated users
def homepage(request):
	#check if user is authenticated
	if request.user.is_authenticated:
		#get schooluser object
		#Check user kind and redirect them to respective page.
		schooluser = request.user.schooluser
		if schooluser.level == "Admin":
			return redirect("admin_homepage")
		elif schooluser.level == "Teacher":
			return redirect("teacher_homepage")
		elif schooluser.level == "Parent":
			return redirect("parents:parents_homepage")
	else:
		#if user is not authenticated go to welcome_page.
		return redirect("accounts:welcome_page")
	
#Welcome page view
def welcome_page(request):
	return render(request,"accounts/welcome_page.html",{})
	
#View to register school and admin information
#Url = /register/
def register(request):
	#form for creating new user
	userform = UserCreationForm()
	#form for admin 
	admin_form = AdminForm()
	#form for school.
	schoolform = SchoolForm()
		
	if request.method== 'POST':
		userform = UserCreationForm(request.POST)
		admin_form = AdminForm(request.POST)
		schoolform = SchoolForm(request.POST)
		#Check if userform, admin_form and schoolform are all valid
		if userform.is_valid() and admin_form.is_valid() and schoolform.is_valid():
			#First save userform, Save function returns saved user
			user = userform.save()
			#after userform is saved
			#Set the user first_name, last_name and email.
			user.first_name = request.POST.get("firstname")
			user.last_name = request.POST.get("lastname")
			user.email = request.POST.get("email")
			user.save()

			#create the schooluser object and assign it to admin
			school_user = SchoolUser(user=user,level="Admin",)
			#Checks if user profile picture is in request files
			if "user-profile-picture" in request.FILES.keys():		
				#set profile from request.FILES to schooluser profile picture attriibute
				school_user.profile_picture=request.FILES.get("user-profile-picture")
			school_user.save()
			
			#Handling admin form 
			admin = admin_form.save(commit=False)
			#assigning manually some fields		
			admin.school_user = school_user
			admin.save()
			#handling form for school
			school = schoolform.save(commit=False)
			#setting school image
			if "school-image" in request.FILES.keys():		
				school.image = request.FILES.get("school-image")

			school.admin = admin
			school.save()
			#save form
			#redirect to login page
			return redirect("accounts:login")
	fname = request.POST.get("firstname")
	lname = request.POST.get("lastname")
	email = request.POST.get("email")
	return render(request, 'accounts/admin_register.html', {'userform':userform,'adminform':admin_form,'schoolform':schoolform,"fname":fname,"lname":lname,"email":email})
	
def send_email(subject,message,recipent):
	if subject and message and recipent:
		try:
			send_mail(subject, message, "links2webcontact@gmail.com", [recipent])
		except BadHeaderError:
			return False
		return True
	else:
		return False


def reset_password(request):
	if "username" in request.GET:
		username = request.GET.get("username")
		try:
			user = User.objects.get(username=username)
		except:
			return HttpResponseServerError("Invalid username entered")
		v_code = "{:06}".format(random.randint(0,999999))
		token = {"v_code":v_code,"username":username}
		print(v_code)
		if not send_email('Schooled password reset verification code','Hello '+username+".\nYour schooled password reset verification code is\n"+ v_code + ".\nPlease note that this code expires after 15 minutes.",user.email):
			return HttpResponseServerError("Something went wrong. Mail failed to send.")

		set_expirable_session(request,username+"-token",token,datetime.now() + timedelta(minutes=15))
		return HttpResponse(user.email)

	if request.method == "POST":
		username = request.POST.get("username")
		v_code = request.POST.get("v-code")
		try:
			token = get_expirable_session(request,username+"-token")
		except:
			return HttpResponseServerError("Verification code has expired. Refresh page to request new one")
		code_valid = (token["username"] == username and token["v_code"] == v_code)
		if code_valid:
			user = User.objects.get(username=username)
			if "new_password1" in request.POST:
				passwordform = SetPasswordForm(user,request.POST)
				if passwordform.is_valid():
					passwordform.save()
					return redirect("accounts:login")
				else:
					return render(request,"accounts/reset-password.html",{"passwordform":passwordform,"v_code":v_code,"username":username})

			else:
				data = Template('''
					{% load crispy_forms_tags %}
					<form method="post" action="{% url 'accounts:reset_password' %}">
					{% csrf_token %}
                    <label><h4 >Username</h4></label>
					<input class="form-control" type="text" name="username"  value="{{username}}" readonly>
					<input type="hidden" name="v-code" value="{{v_code}}" >
					{{passwordform|crispy}}
					<button type="submit" class="genric-btn primary w-100 radius">Submit</button>
					</form>
					''').render(RequestContext(request,{"v_code":v_code,"username":username,"passwordform":SetPasswordForm(user)}))
				return HttpResponse(data)
		else:
			return HttpResponseServerError("Invalid verification code")

	return render(request,"accounts/reset-password.html",{})
	
#Class based view to handle login
class account_login(LoginView):
	template_name = "accounts/login.html"
	next = "account:account_handlers"
	
#redirect users to thier respectful homepages
def account_handler(request):
	try:
		if request.user.schooluser.level=='Admin':
			return redirect('admin_homepage')
		elif request.user.schooluser.level=='Teacher':
			return redirect('teacher_homepage')
		elif request.user.schooluser.level=='Parent':
			return redirect("parents:parents_homepage")
	except:
		return redirect("accounts:welcome_page")

	
