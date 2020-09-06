import random
from datetime import datetime,timedelta
from django.shortcuts import render, redirect,HttpResponse
from django.http.response import HttpResponseNotAllowed,HttpResponseServerError
from django.contrib.auth import get_user_model
from .forms import UserCreationForm,SetPasswordForm
from django.core.mail import send_mail,BadHeaderError
from django.contrib.auth.views import LoginView
from django.template import Template,RequestContext,Context
from django.contrib import messages
from admins.forms import AdminForm,SchoolForm
from django.contrib import messages
from tools import get_expirable_session,set_expirable_session,save_picture
from .models import help
# Create your views here.
#main homepage
#redirects authenticated users
def homepage(request):
	#check if user is authenticated
	if request.user.is_authenticated:
		#get schooluser object
		#Check user kind and redirect them to respective page.
		user = request.user
		if user.level == "Admin":
			return redirect("admin_homepage")
		elif user.level == "Teacher":
			return redirect("teacher_homepage")
		elif user.level == "Parent":
			return redirect("parents:parents_homepage")
	else:
		#if user is not authenticated go to welcome_page.
		return redirect("accounts:welcome_page")
	
#Welcome page view
def welcome_page(request):
	return render(request,"accounts/welcome_page.html",{})

def about_view(request):
	return render(request,"accounts/about_page.html",{})

#View to register school and admin information
#Url = /register/
def register(request):
	#form for creating new user
	userform = UserCreationForm()
	#Set first_name,last_name,email fields to be required
	userform.fields['first_name'].required = userform.fields['last_name'].required = userform.fields['email'].required = True
	admin_form = AdminForm()
	schoolform = SchoolForm()
	if request.method== 'POST':
		userform = UserCreationForm(request.POST)
		admin_form = AdminForm(request.POST)
		schoolform = SchoolForm(request.POST)
		#Check if userform, admin_form and schoolform are all valid
		if userform.is_valid() and admin_form.is_valid() and schoolform.is_valid():
			#Get user model object,assign level, set image and save
			user = userform.save(commit=False)
			user.level = "Admin"
			user.save()
			save_picture(user.profile_picture,request.FILES.get("user-profile-picture"))
			#Get admin model object,assign to user and save
			admin = admin_form.save(commit=False)	
			admin.user = user
			admin.save()
			#Get school model object, save image, assign school adkin and save
			school = schoolform.save(commit=False)
			school.admin = admin
			school.save()
			#setting school image
			save_picture(school.image,request.FILES.get("school-image"))
			#Messages to be added
			#redirect to login page
			messages.success(request,"Your school has been registered successfully. Kindly login to continue")
			request.session[user.username + "_new_user"] = True
			return redirect("accounts:login")
	return render(request, 'accounts/admin_register.html', {'userform':userform,'adminform':admin_form,'schoolform':schoolform,})
	
#Functiom that uses django mail api to send email
def send_email(subject,message,recipent):
	if subject and message and recipent:
		try:
			send_mail(subject, message, "links2webcontact@gmail.com", [recipent])
		except BadHeaderError:
			return False
		return True
	else:
		return False

#Reset password view
def reset_password(request):
	#If the key username is in GET request
	if "username" in request.GET:
		username = request.GET.get("username")
		#Try to get the username
		#On exception return server error
		try:
			user = get_user_model().objects.get(username=username)
		except:
			return HttpResponseServerError("Invalid username entered")
		#Assign v_code to generated 6 digits value
		v_code = "{:06}".format(random.randint(0,999999))
		token = {"v_code":v_code,"username":username}
		#Try to send email else return server error
		if not send_email('Schooled password reset verification code','Hello '+username+".\nYour schooled password reset verification code is\n"+ v_code + ".\nPlease note that this code expires after 15 minutes.",user.email):
			return HttpResponseServerError("Something went wrong. Mail failed to send.")
		#Set token object in expirable session to expire after 15 minutes
		set_expirable_session(request,username+"-token",token,datetime.now() + timedelta(minutes=15))
		#Return user email
		return HttpResponse(user.email)
	#On post requet
	if request.method == "POST":
		#Get username and v_code
		username = request.POST.get("username")
		v_code = request.POST.get("v-code")
		#Try to get token  or return server error
		try:
			token = get_expirable_session(request,username+"-token")
		except:
			return HttpResponseServerError("Verification code has expired. Refresh page to request new one")
		#Compare saved username and v_code with  inputed values
		code_valid = (token["username"] == username and token["v_code"] == v_code)
		if code_valid:
			#Get user model object
			user = get_user_model().objects.get(username=username)
			#Password form is submitted
			if "new_password1" in request.POST:
				passwordform = SetPasswordForm(user,request.POST)
				if passwordform.is_valid():
					passwordform.save()
					messages.success(request,"Your password has been successfully reset.")
					return redirect("accounts:login")
				else:
					return render(request,"accounts/reset-password.html",{"passwordform":passwordform,"v_code":v_code,"username":username})

			else:
				#Create a set password form template
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
				#Return template
				return HttpResponse(data)
		else:
			#If code_valid is False, return server error
			return HttpResponseServerError("Invalid verification code")

	return render(request,"accounts/reset-password.html",{})
	
#Class based view to handle login
class account_login(LoginView):
	template_name = "accounts/login.html"
	next = "account:account_handlers"
	
#redirect users to thier respectful homepages
def account_handler(request):
	try:
		if request.user.level=='Admin':
			return redirect('admin_homepage')
		elif request.user.level=='Teacher':
			return redirect('teacher_homepage')
		elif request.user.level=='Parent':
			return redirect("parents:parents_homepage")
	except:
		return redirect("accounts:welcome_page")

def help_view(request):
    if "help_pk" in request.GET:
        help_obj = help.objects.get(pk=request.GET.get("help_pk"))
        description = Template("{{desc|linebreaks}}").render(Context({"desc":help_obj.description}));
        return HttpResponse(description)
    helps = help.objects.all()
    return render(request,"accounts/help-page.html",{"helps":helps})
