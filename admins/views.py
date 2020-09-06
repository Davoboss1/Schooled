from django.shortcuts import render, redirect
from django.db.utils import IntegrityError
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import check_password
from django.contrib import messages as django_messages
from .forms import SchoolForm, AdminForm
from teachers.models import Class,Teacher
from teachers.forms import TeacherForm
from .models import Admin,School,Messages,Conversation
from accounts.forms import UserCreationForm,UserUpdateForm
from django.template.loader import render_to_string
from django.template import Template,Context
from django.http.response import HttpResponse,HttpResponseNotFound,HttpResponseServerError,JsonResponse
from django.urls import reverse
from students.models import Student,Attendance,Term
from django.core.paginator import Paginator,EmptyPage
from django.http.response import Http404,HttpResponseServerError
from django.core.exceptions import ValidationError
from django.db.models import Q
from tools import require_ajax,view_for,save_picture,require_auth
from students.models import School_activity_log

# Create your views here.
#Writes from error in string of h6 tags
def get_errors_in_text(form):
	errors_dict = form.errors.as_data()
	error_text = ""
	for keys in errors_dict.keys():
		error_text += f"<h6 class='py-2 text-center' > {errors_dict[keys][0].messages[0]} </h6>"
	return error_text
	
#school_owner or admin homepage
@view_for("admin")
def school_owner_home_page(request):
	user = request.user
	#Gets user unread messages
	unread_msg_count = Messages.objects.filter(Q(conversation__reciever=user) | Q(conversation__sender=user.get_username()),message_read=False).exclude(sent_by=user.get_username()).count()

	#Gets all user schools
	schools = request.user.admin.schools.all()
	#Gets all schools unread notifications number at set it to a new attribute notif_count
	for school in schools:
		school.notif_count = School_activity_log.objects.filter(Class__school=school,viewed=False).count()
	#School form for creating new form
	sch_form = SchoolForm()
	#Default notif_count to be shown.
	#Gets notif_count of first school
	try:
		notif_count = schools.first().notif_count
	except:
		notif_count = 0
	new_user = request.session.get(user.username + "_new_user")
	if new_user:
		del request.session[user.username+"_new_user"]
	return render(request,"admins/school_owner_admin_page.html",{'user':request.user,"unread_msg_count":unread_msg_count,"unviewed_notifications_count":notif_count,"schoolform":sch_form,"schools":schools,"new_user":new_user})


#View for creating a new school
@view_for("admin")
@require_ajax
def create_new_school(request):
	sch_form = SchoolForm(request.POST)
	if sch_form.is_valid():
		sch = sch_form.save(commit=False)
		#Get admin object and set it as the admin of newly create school
		admin = request.user.admin
		sch.admin = admin
		sch.save()		
		save_picture(sch.image,request.FILES.get("school-image"))
		return JsonResponse({"name":sch.school_name,"pk":sch.pk,"motto":sch.motto})
	else:
		return HttpResponseServerError(get_errors_in_text(sch_form))
	
#Delete school view (Obvi)
@view_for("admin")
@require_ajax
def delete_school(request):
	#Get password and verify if its user correct password
	password = request.POST.get("password")
	valid_password = check_password(password,request.user.password)
	if valid_password:
		#If valid password.
		#Get school by admin and pk and delete it.
		sch_pk = request.POST.get("sch_pk")
		School.objects.get(admin=request.user.admin,pk=sch_pk).delete()
		return HttpResponse("Deleted successfully")
	else:
		#return server error
		#WP = Wrong Password
		return HttpResponseServerError("WP")
	
#This view does three things.
#Views school and admin information from admin page.
#Changes school information.
#Changes admin information.
#Changes admin password.
#Basically it performs all functions on the school profile page
@view_for("admin")
@require_ajax
def school_profile(request,sch_pk):
	current_user = request.user
	admin = current_user.admin
	school = admin.schools.get(pk=sch_pk)
	if request.method == "POST":
		#fortype contains type of action to be performed.
		formtype = request.POST.get("formtype")
		if formtype == "school":
			#Updates school information
			form = SchoolForm(request.POST,instance = school)
			if form.is_valid():
				form = form.save()
				save_picture(form.image,request.FILES.get("sch-logo"))
				return HttpResponse("Success")
			else:
				#Returns form erros
				return HttpResponseServerError(get_errors_in_text(form))
		elif formtype == "admin":
			#Updates admin and user information
			form = UserUpdateForm(request.POST,instance=current_user)
			admin_form = AdminForm(request.POST,instance=current_user.admin)
			if form.is_valid() and admin_form.is_valid():
				form = form.save()
				#for handling profile picture upload
				save_picture(form.profile_picture,request.FILES.get("user-profile-picture"))
				admin_form.save()
				return HttpResponse("Success")
			else:
				return HttpResponseServerError(get_errors_in_text(form) + get_errors_in_text(admin_form))
		elif formtype == "password":
			#Changes password
			#Updates password with password change form
			form = PasswordChangeForm(current_user,request.POST)
			if form.is_valid():
				form.save()
				return HttpResponse("Success")
			else:
				return HttpResponseServerError(get_errors_in_text(form))
	#This checks get request for formtype and renders type of form requested.
	#I.e : if type is school return page with school form.

	if request.GET.get("type")=="school":
		return render(request,"admins/update-school-and-admin.html",{"form":SchoolForm(instance=school),"type":"school",},)
	elif request.GET.get("type")=="admin":
		return render(request,"admins/update-school-and-admin.html",{"form":AdminForm(instance=current_user.admin),"userform":UserUpdateForm(instance=current_user),"type":"admin",})
	elif request.GET.get("type")=="password":
		return render(request,"admins/update-school-and-admin.html",{"form": PasswordChangeForm(current_user),"type":"password", },)

	students_no = Student.objects.filter(Class__school = school).count()
	teachers_no = Teacher.objects.filter(teacher_class__school = school).count()

	return render(request,"admins/school_profile.html",{'user':current_user,"school":school,"students_no":students_no,"teachers_no":teachers_no})
	
#view which shows list of all classes
@view_for("admin")
@require_ajax
def class_list(request,sch_pk,type):
	admin = request.user.admin
	school = School.objects.get(admin=admin,pk=sch_pk)
	link_url = reverse(type)
	
	if type == "manage_teachers":
		#if type is manage_teacher
		user_form = UserCreationForm()
		user_form.fields['first_name'].label += " (Optional)"
		user_form.fields['last_name'].label += " (Optional)"
		user_form.fields['email'].label += " (Optional)"
	else:
		#if type is not manage_teachers
		#assign user form variables to none
		user_form=None
		
	#Get a list of all classes in school
	all_class = school.class_set.all()
	return render(request,"admins/class-list.html",{"url":link_url,'user':request.user,'type':type,'userform':user_form,"classes":all_class,"current_term":Term.objects.filter(school=school,current_session=True).first(),"school":school})
	
#view that handles performance viewing for admin
@view_for("admin")
@require_ajax
def view_performance(request,pk):
	admin = request.user.admin
	#Get current class by pk
	current_class = Class.objects.get(pk=pk,school__admin=admin)
	#get all students in current_class
	students_in_class = current_class.student_set.all()
	terms = Term.objects.filter(school=current_class.school.pk)
	current_term = terms.get(current_session=True)
	context = {"all_students":students_in_class,"class_pk":pk,"terms":terms,"current_term":current_term}

	#Pagination
	if "page" in request.GET.keys():
		#Paginator object to show only 10 objects
		paginator = Paginator(students_in_class,10)
		students_in_class = paginator.get_page(request.GET.get("page"))
		
		context["all_Info"] = students_in_class
		context['url'] = reverse("view_performance",kwargs={"pk":pk})
		
		if "year" in request.GET.keys() and "term" in request.GET.keys():
			year = int(request.GET.get("year"))
			term_text = request.GET.get("term")
			#try to get term object
			try:
				term = Term.objects.get(school=current_class.school.pk,year=year,term=term_text)
			except Term.DoesNotExist:
				return HttpResponse("DOE_ERROR")
			#get all students in the paginated object list
			for student in students_in_class.object_list:
				#filter the performance by term
				filtered_performance = list(student.performance_set.filter(term=term))
				#create new attribute called termly_performance
				student.termly_performance = filtered_performance
		return render(request,"students/pagination/performance_page.html",context)
	else:
		paginator = Paginator(students_in_class,10)
		students_in_class = paginator.get_page(1)
		context["all_students"] = students_in_class
		
	#This occurs when user load more performance of a particular student
	if "student_pk" in request.GET.keys():
		student = Student.objects.get(Class=current_class,pk=int(request.GET.get("student_pk")))
		year = int(request.GET.get("year"))
		term_text = request.GET.get("term")
		#try to get term object
		term = Term.objects.get(school=student.Class.school,year=year,term=term_text)
		filtered_performance = list(student.performance_set.filter(term=term))
		#create new attribute called termly_performance
		student.termly_performance = filtered_performance
		return HttpResponse(loadmore_performance(student.termly_performance,10,int(request.GET.get("page_no"))))
	return render(request,"admins/view-student-performance.html",context)
	
#Function that paginages queryset but mainly performance and returns it in html table rows
def loadmore_performance(queryset,no_of_items,page):
	paginator = Paginator(queryset,no_of_items)
	try:
		queryset = paginator.page(page).object_list
	except EmptyPage:
		return HttpResponse("Empty",status=404)
	data = ""
	for performance in queryset:
		data+=f'''<tr>
<td>{performance.subject}</td>
<td>{performance.test}</td>
<td>{performance.exam}</td>
<td>{performance.total}</td>
<td>{performance.comment}</td>
</tr>
		'''
	return data
		
#view for viewing attendance for admin
@view_for("admin")
@require_ajax
def view_attendance(request,pk):
	admin = request.user.admin
	#Get current class by pk
	current_class = Class.objects.get(pk=pk,school__admin=admin)
	#get all students in current_class
	students_in_class = current_class.student_set.all()
	paginator = Paginator(students_in_class,10)
	students_in_class = paginator.get_page(request.GET.get("page"))
	#get all attendance for current_class
	class_attendance = current_class.attendance_set.all()
	return render(request,"admins/view-student-attendance.html",{"all_students":students_in_class,"attendance":class_attendance,"class_pk":pk})
	
#view to view students profile or info
#Used by admin and teacher
@require_auth
def view_student_info(request,**kwargs):
	#if admin wants to view students info.
	#get selected class by pk
	if "pk" in kwargs.keys():
		admin = request.user.admin
		students = Class.objects.get(pk=kwargs['pk'],school__admin=admin).student_set.all()
	else:
		#if teacher wants to view student info, Just view students in his class
		students = request.user.teacher.teacher_class.student_set.all()
	return render(request,"admins/Student_info.html",{"all_students":students})
	
	
# View to manage teachers.
@view_for("admin")
@require_ajax
def manage_teachers(request,class_pk):
	selected_class = Class.objects.get(pk=class_pk)
	#form for updating teacher info
	form= TeacherForm(instance = selected_class.teacher)
	#if class has no teacher
	if selected_class.teacher == None:
		#Return template with "No teacher in class" message
		return HttpResponse(f'''<div class="alert alert-warning my-3" role="alert">
  No teacher for this class. <a href="#add-teachers" data-toggle="collapse" class="alert-link" onclick="add_class('{selected_class.class_name}');" >Click here to add teacher</a>. 
</div>''')

	return render(request,"admins/manage-teachers-or-parents.html",{"type":"Teacher","teacher":selected_class.teacher,"form":form})
	
#view to manage parents
@view_for("admin")
@require_ajax
def manage_parents(request,class_pk):
	selected_class = Class.objects.get(pk=class_pk)
	#get all students. 
	#To view their parents
	students = selected_class.student_set.all()
	paginator = Paginator(students,10)
	students = paginator.get_page(request.GET.get("page"))
	return render(request,"admins/manage-teachers-or-parents.html",{"type":"Parent","students":students,"class_pk":class_pk,})


#View that lists all conversations
#View handles all conversation requests and differenciates requests by arguments in get request
@require_auth
@require_ajax
def message_list(request,sch_pk=None):
	#Get conversations in which the user is either the sender or the reciever
	conversations = Conversation.objects.filter(sender=request.user.get_username()) | Conversation.objects.filter(reciever=request.user)
	user = request.user
	if request.is_ajax() and request.method == "POST":
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
@require_ajax
def messages(request,convo_pk):
	user = request.user
	#Get conversation by pk
	conversation = Conversation.objects.get(Q(pk=convo_pk),Q(sender=user.get_username()) | Q(reciever=user))
	if request.is_ajax():
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
@require_ajax
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
@require_ajax
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
@require_ajax
def check_msg(request,convo_pk):
	user = request.user
	conversation = Conversation.objects.get(Q(pk=convo_pk),Q(sender=user.get_username()) | Q(reciever=user))
	#Get messages sent by other person that hasn't been read yet
	msgs = conversation.messages_set.filter(message_read=False).exclude(sent_by=request.user.get_username())
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
	msgs.update(message_read=True)
	return HttpResponse(data)

#Notifications view
@view_for("admin")
@require_ajax
def notifications(request,sch_pk):
	admin = request.user.admin 
	school = School.objects.get(pk=sch_pk,admin=admin)
	#Get school activity_log or notifications
	activity_log = School_activity_log.objects.filter(Class__school=school)
	#Get total number of notifications
	total_no = activity_log.count()
	#Update the activity_log or notifications as viewed
	School_activity_log.objects.filter(Class__school=school,viewed=False).update(viewed=True)
	#Show only 20 notifications at once
	activity_log_paginator = Paginator(activity_log,20)
	if "page" in request.GET:
		#If more notifications are requested
		try:
			page = request.GET.get("page")
			activity_log = activity_log_paginator.page(page)
			res = ""
			for activity in activity_log:
				#Notification template
				res += f'''
			<blockquote class="generic-blockquote mt-3" style="background-color:#f2f2f2;">                           <h6 >Date : {activity.Activity_date_and_time.date}</h6>
			<hr>
			<h6>Time : {activity.Activity_date_and_time.time}</h6>
			<hr>
			<b class="text-dark">{activity.Activity_info}</b>
			</blockquote>
			'''
			return HttpResponse(res)

		except EmptyPage:
			return HttpResponseServerError("EMPTY")
	else:
		activity_log = activity_log_paginator.page(1)
	return render(request,"admins/notifications.html",{"activity_log":activity_log,"total_no":total_no})

#View for showing student profile
@require_auth
def profile_page(request,pk):
	user = request.user
	level = user.level
	if level == "Parent":
		student =  user.parent.student_set.get(pk=pk)
	elif level == "Admin":
		student = Student.objects.get(Class__school__admin=user.admin,pk=pk)
	else:
		student = user.teacher.teacher_class.student_set.get(pk=pk)
	attendance = student.Class.attendance_set.all()
	terms = Term.objects.filter(school=student.Class.school)
	if terms.exists():
		current_term = terms.get(current_session=True)
	else:
		current_term = None
	return render(request,"admins/profile_page.html",{"student":student,"all_attendance" : attendance,"current_term":current_term,"terms":terms,})

def  coming_soon(request,pk):
	return render(request,"admins/coming_soon.html",{})

#View for creating new term or sessions
@view_for("admin")
@require_ajax
def add_sessions(request,sch_pk):
	if request.method == "POST":
		year = request.POST.get("year")
		term = request.POST.get("term")
		school = School.objects.get(admin=request.user.admin,pk=sch_pk)
		term_obj = Term.objects.filter(school=school,year=year,term=term)
		if term_obj.exists():
			current_term = term_obj.first()
			print("Session exists")
		else:
			current_term = Term.objects.create(school=school,year=year,term=term)
			print("New session")
			
		current_term.set_as_current()
		return HttpResponse("Success")

#View for showing teacher or admin or parents profile
@require_auth
@require_ajax
def show_profile(request,type,lookup):
	if type == "school":
		sch = School.objects.get(pk=lookup)
		admin = sch.admin
		return render(request,"admins/show-school-profile.html",{"admin":admin,"school":sch})
	elif type == "teacher":
		teacher = get_user_model().objects.get(username=lookup).teacher
		return render(request,"teachers/show-teachers-profile.html",{"teacher":teacher})
	elif type == "parent":
		parent = get_user_model().objects.get(username=lookup).parent



		return render(request,"parents/show-parent-profile.html",{"parent":parent})
