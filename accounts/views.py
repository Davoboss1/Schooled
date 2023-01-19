import random
from datetime import datetime,timedelta
from django.shortcuts import render, redirect,HttpResponse
from django.http.response import HttpResponseNotAllowed,HttpResponseServerError,JsonResponse
from django.contrib.auth import get_user_model
from .forms import UserCreationForm,SetPasswordForm
from django.core.mail import send_mail,BadHeaderError
from django.core.paginator import Paginator,EmptyPage
from django.contrib.auth.views import LoginView
from django.template import Template,RequestContext,Context
from django.contrib import messages as django_messages
from admins.forms import AdminForm,SchoolForm
from django.contrib import messages
from django.db.models import Q
from tools import get_expirable_session,set_expirable_session,save_picture,require_auth,require_ajax
from .models import help,Messages,Conversation
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
			django_messages.success(request,"Your school has been registered successfully. Kindly login to continue")
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
					django_messages.success(request,"Your password has been successfully reset.")
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


#View that lists all conversations
#View handles all conversation requests and differenciates requests by arguments in get request
@require_auth

def message_list(request,sch_pk=None):
	#Get conversations in which the user is either the sender or the reciever
	conversations = Conversation.objects.filter(sender=request.user.get_username()) | Conversation.objects.filter(reciever=request.user)
	user = request.user
	if request.method == "POST":
		#Request for creating new conversation
		if "convo" in request.POST:
			return new_conversation(request)

	#Counts unread messages in each conversation
	for convo in conversations:
		convo.msg_count = convo.messages_set.filter(message_read=False).exclude(sent_by=request.user.get_username()).count()

	return render(request,"admins/message-list.html",{"conversations":conversations,"user":user,})

#View that lists all messages
#View handles all messaging requests and differenciates requests by arguments in get request
@require_auth

def messages(request,convo_pk):
	user = request.user
	#Get conversation by pk
	conversation = Conversation.objects.get(Q(pk=convo_pk),Q(sender=user.get_username()) | Q(reciever=user))
	if "more_msg" in request.GET:
		#Request for loading more messages
		return more_msg(request,convo_pk)
	elif "check_msg" in request.GET:
		#Request for checking for new messages
		return check_msg(request,convo_pk)
	#If it was a post request.
	#A new message was sent
	if request.POST:
		message = Messages(conversation=conversation,message=request.POST.get("message"),sent_by=request.POST.get("sender"))
		message.save()
		return HttpResponse("Success")

	msgs = conversation.messages_set.all()
	#Paginate messages i.e show only 16 messages at once
	paginator = Paginator(msgs,16)
	msgs = paginator.page(1)
	msgs = list(msgs.object_list)
	#Reverse the list to show latest messages at the bottom
	msgs.reverse()	
	#Update unread messages as read
	conversation.messages_set.all().exclude(sent_by=request.user.get_username()).update(message_read=True)
	return render(request,"admins/messages.html",{"conversation":conversation,"user":user,"msgs":msgs})

#Funtion for creating new conversation
@require_auth

def new_conversation(request):
	try:
		#Try to check if new conversation exactly matches an old conversation
		conversation = Conversation.objects.filter(sender=request.POST.get("sender"),reciever=get_user_model().objects.get(username=request.POST.get("username-entry")),subject__iexact=request.POST.get("subject-entry")) | Conversation.objects.filter(sender=request.POST.get("username-entry"),reciever=get_user_model().objects.get(username=request.POST.get("username-entry")),subject__iexact=request.POST.get("subject-entry"))
		#If conversation already exists, Just select conversation instead of creating duplicate
		if conversation.exists():
			conversation = conversation.first()
		else:
			conversation = Conversation(sender=request.POST.get("sender"),reciever=get_user_model().objects.get(username=request.POST.get("username-entry")),subject=request.POST.get("subject-entry"))
		conversation.save()
	except get_user_model().DoesNotExist:
		#If Conversation had an invalid username
		return HttpResponseServerError("Invalid user name entered")	
	#Add message to conversation
	message = Messages(conversation=conversation,message=request.POST.get("message-entry"),sent_by=request.POST.get("sender"))
	message.save()
	return HttpResponse("Success")

#function for loading more messages
@require_auth

def more_msg(request,convo_pk):
	user = request.user
	page_no = int(request.GET.get("page_no"))
	conversation = Conversation.objects.get(Q(pk=convo_pk),Q(sender=user.get_username()) | Q(reciever=user))
	messages = conversation.messages_set.all()
	paginator = Paginator(messages,16)
	try:
		data = paginator.page(page_no)
	except EmptyPage:
		return HttpResponse("Empty")
	data = list(data.object_list)
	data.reverse()			
	#Message template
	data = Template('''
{% load custom_filter %}
		{% for msg in messages_set %} 	
    {% if msg.sent_by == user.get_username %}
    <div class="ml-auto d-flex flex-column" style="width: 70%;padding: 0;">
      <div class="d-flex flex-column"
        style="background: linear-gradient(#330033 90%,white 0); border-radius: 5px;">
        <p class="text-light p-3 m-0">
          {{msg.message}}
        </p>
        <div class="thumb m-0 ml-auto">
          <img class="rounded-circle" style="width: 35px; height: 35px;" alt="" src="{{user.profile_picture.url}}">
        </div>

      </div>
      <small class="text-muted ml-auto" style="text-align: end;">{{msg.message_datetime|timesince }} ago</small>

    </div>
    {% else %}
    <div class="mr-auto" style="width: 70%;padding: 0;">
      <div class="d-flex flex-column"
        style="background: linear-gradient(black 90%,white 0); border-radius: 5px;">
        <p class="text-light p-3 m-0">
          {{msg.message}}
        </p>
        <div class="thumb m-0 mr-auto">
          {% if conversation.sender == user.get_username %}
          <img class="rounded-circle" style="width: 35px; height: 35px;" alt="" src="{{conversation.reciever.profile_picture.url}}">
          {% else %}
          {% with other_user=conversation.sender|get_user %}
          <img class="rounded-circle" style="width: 35px; height: 35px;" alt="" src="{{other_user.profile_picture.url}}">
          {% endwith %}
          {% endif %}
        </div>
      </div>
      <small class="text-muted mr-auto">{{msg.message_datetime|timesince }} ago</small>
    </div>
    {% endif %}
		{% endfor %}
				 ''').render(Context({"messages_set" : data,"user":user,"conversation":conversation}))
	return JsonResponse({"next_page_no":page_no+1,"data" : data})

#Function to check for new messages
@require_auth

def check_msg(request,convo_pk):
	user = request.user
	conversation = Conversation.objects.get(Q(pk=convo_pk),Q(sender=user.get_username()) | Q(reciever=user))
	#Get messages sent by other person that hasn't been read yet
	msgs_set = conversation.messages_set.filter(message_read=False).exclude(sent_by=request.user.get_username())
	msgs = list(msgs_set)
	msgs.reverse()			
	#Message template
	data = Template('''
{% load custom_filter %}
		{% for msg in messages_set %} 	
    <div class="mr-auto" style="width: 70%;padding: 0;">
      <div class="d-flex flex-column"
        style="background: linear-gradient(black 90%,white 0); border-radius: 5px;">
        <p class="text-light p-3 m-0">
          {{msg.message}}
        </p>
        <div class="thumb m-0 mr-auto">
          {% if conversation.sender == user.get_username %}
          <img class="rounded-circle" style="width: 35px; height: 35px;" alt="" src="{{conversation.reciever.profile_picture.url}}">
          {% else %}
          {% with other_user=conversation.sender|get_user %}
          <img class="rounded-circle" style="width: 35px; height: 35px;" alt="" src="{{other_user.profile_picture.url}}">
          {% endwith %}
          {% endif %}
        </div>
      </div>
      <small class="text-muted mr-auto">{{msg.message_datetime|timesince }} ago</small>
    </div>
		{% endfor %}
				 ''').render(Context({"messages_set" : msgs,"user":user,"conversation":conversation}))
	msgs_set.update(message_read=True)
	return HttpResponse(data)


#View for help page
def help_view(request):
    #If help_pk attr is in request.GET return requested help description 
    if "help_pk" in request.GET:
        help_obj = help.objects.get(pk=request.GET.get("help_pk"))
        description = Template("{{desc|linebreaks}}").render(Context({"desc":help_obj.description}));
        return HttpResponse(description)
    #Get all help and return template
    helps = help.objects.all()
    return render(request,"accounts/help-page.html",{"helps":helps})
