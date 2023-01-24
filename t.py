de6d3b9:students/views.py:import os
de6d3b9:students/views.py:import csv
de6d3b9:students/views.py:from django.shortcuts import render,redirect,get_object_or_404,Http404,HttpResponse,reverse
de6d3b9:students/views.py:from django.http.response import HttpResponseServerError
de6d3b9:students/views.py:from .models import Student, Performance, Attendance,Term
de6d3b9:students/views.py:from teachers.models import Teacher
de6d3b9:students/views.py:from admins.models import Admin
de6d3b9:students/views.py:from admins.views import loadmore_performance
de6d3b9:students/views.py:from parents.models import Parent
de6d3b9:students/views.py:from django.db.models import Q
de6d3b9:students/views.py:from accounts.forms import UserCreationForm
de6d3b9:students/views.py:from django.contrib.auth import get_user_model
de6d3b9:students/views.py:from .forms  import StudentForm, PerformanceForm
de6d3b9:students/views.py:from django.contrib import messages
de6d3b9:students/views.py:from django.views.generic.edit import DeleteView
de6d3b9:students/views.py:from django.urls import reverse_lazy
de6d3b9:students/views.py:from django.template.loader import render_to_string,get_template
de6d3b9:students/views.py:from django.template import Context,Template
de6d3b9:students/views.py:from datetime import datetime,date,timedelta
de6d3b9:students/views.py:from django.utils.timezone import localdate
de6d3b9:students/views.py:from django.core.paginator import Paginator
de6d3b9:students/views.py:from xhtml2pdf import pisa
de6d3b9:students/views.py:from io import StringIO
de6d3b9:students/views.py:from schooled import settings
de6d3b9:students/views.py:from tools import view_for,require_ajax,require_auth
de6d3b9:students/views.py:#FUNCTION BASED VIEWS
de6d3b9:students/views.py:#View for viewing performance
de6d3b9:students/views.py:#Used by teachers
de6d3b9:students/views.py:@view_for("teacher")
de6d3b9:students/views.py:def performance_page(request,type):
de6d3b9:students/views.py:	school = request.user.teacher.teacher_class.school
de6d3b9:students/views.py:	context={
de6d3b9:students/views.py:		'type':type,
de6d3b9:students/views.py:		"terms":Term.objects.filter(school=school),
de6d3b9:students/views.py:		'current_term':Term.objects.filter(school=school,current_session=True).first()
de6d3b9:students/views.py:	}
de6d3b9:students/views.py:	#Pagination of students
de6d3b9:students/views.py:	if "page" in request.GET.keys():
de6d3b9:students/views.py:		#get all students in teachers class
de6d3b9:students/views.py:		all_Info= request.user.teacher.teacher_class.student_set.all()
de6d3b9:students/views.py:		
de6d3b9:students/views.py:		#Paginate students, Show only 10 objects
de6d3b9:students/views.py:		paginator = Paginator(all_Info,10)
de6d3b9:students/views.py:		all_Info = paginator.get_page(request.GET.get("page"))
de6d3b9:students/views.py:		#assign variables to context
de6d3b9:students/views.py:		context["all_Info"] = all_Info
de6d3b9:students/views.py:		#If type of request is edit-performance just render edit-performance template
de6d3b9:students/views.py:		if type == "edit-performance":
de6d3b9:students/views.py:			teacher_class = request.user.teacher.teacher_class
de6d3b9:students/views.py:			available_subjects = teacher_class.performance_set.only("subject").values_list('subject',flat=True).distinct()
de6d3b9:students/views.py:			context["available_subjects"] = available_subjects
de6d3b9:students/views.py:			return render(request,"students/pagination/edit-performance.html",context)
de6d3b9:students/views.py:		else:
de6d3b9:students/views.py:			context['url'] = reverse("students:performance_page",kwargs={"type":"view-performance"})
de6d3b9:students/views.py:			#get year and term value
de6d3b9:students/views.py:			if "year" in request.GET.keys() and "term" in request.GET.keys():
de6d3b9:students/views.py:				#try to get term object
de6d3b9:students/views.py:				try:
de6d3b9:students/views.py:					year = int(request.GET.get("year"))
de6d3b9:students/views.py:					term_text = request.GET.get("term")
de6d3b9:students/views.py:					term = Term.objects.get(year=year,term=term_text,school=school)
de6d3b9:students/views.py:				except Term.DoesNotExist:
de6d3b9:students/views.py:					return HttpResponse("DOE_ERROR")
de6d3b9:students/views.py:				except ValueError:
de6d3b9:students/views.py:					return HttpResponseServerError("Invalid session detected")
de6d3b9:students/views.py:				#get all students in the paginated object list
de6d3b9:students/views.py:				for student in all_Info.object_list:
de6d3b9:students/views.py:					#filter the performance by term
de6d3b9:students/views.py:					filtered_performance = list(student.performance_set.filter(term=term))
de6d3b9:students/views.py:					#create new attribute called termly_performance
de6d3b9:students/views.py:					student.termly_performance = filtered_performance			
de6d3b9:students/views.py:			return render(request,"students/pagination/performance_page.html",context)
de6d3b9:students/views.py:	#If performance for particular student
de6d3b9:students/views.py:	#Mainly for loading more performances
de6d3b9:students/views.py:	if "student_pk" in request.GET.keys():
de6d3b9:students/views.py:		student = Student.objects.get(pk=int(request.GET.get("student_pk")))
de6d3b9:students/views.py:		year = int(request.GET.get("year"))
de6d3b9:students/views.py:		term_text = request.GET.get("term")
de6d3b9:students/views.py:		#try to get term object
de6d3b9:students/views.py:		term = Term.objects.get(year=year,term=term_text,school=school)
de6d3b9:students/views.py:		filtered_performance = list(student.performance_set.filter(term=term))
de6d3b9:students/views.py:		#create new attribute called termly_performance
de6d3b9:students/views.py:		student.termly_performance = filtered_performance
de6d3b9:students/views.py:		return HttpResponse(loadmore_performance(student.termly_performance,10,int(request.GET.get("page_no"))))
de6d3b9:students/views.py:	context["students"] = request.user.teacher.teacher_class.student_set.all()
de6d3b9:students/views.py:	return render(request, 'students/performance_page.html', context)
de6d3b9:students/views.py:#Function for STUDENTS ATTENDANCE
de6d3b9:students/views.py:@view_for("teacher")
de6d3b9:students/views.py:def attendance_page(request,type):
de6d3b9:students/views.py:	#get all student in in teachers class
de6d3b9:students/views.py:	all_Info= request.user.teacher.teacher_class.student_set.all()
de6d3b9:students/views.py:	current_class = request.user.teacher.teacher_class
de6d3b9:students/views.py:	Date =localdate()
de6d3b9:students/views.py:	#if a particular date is requested
de6d3b9:students/views.py:	if "date" in request.GET.keys():
de6d3b9:students/views.py:		#get requested date
de6d3b9:students/views.py:		Date = request.GET.get("date")
de6d3b9:students/views.py:		#try to get attendance by date and class
de6d3b9:students/views.py:		try:
de6d3b9:students/views.py:			attendance_object = Attendance.objects.get(date=Date,Class=current_class)
de6d3b9:students/views.py:			attendance = attendance_object.present_students.all()
de6d3b9:students/views.py:			
de6d3b9:students/views.py:		#if attendance does'nt exist
de6d3b9:students/views.py:		except Attendance.DoesNotExist:
de6d3b9:students/views.py:		
de6d3b9:students/views.py:			date_list = Date.split("-")
de6d3b9:students/views.py:			Date = date(int(date_list[0]),int(date_list[1]),int(date_list[2]))
de6d3b9:students/views.py:			#if date is in future
de6d3b9:students/views.py:			if Date > localdate():
de6d3b9:students/views.py:				return HttpResponseServerError('<div class="alert alert-danger alert-dismissible fade show" role="alert"><strong>Oops! sorry</strong> You can\'t add or view date for the future .<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>')
de6d3b9:students/views.py:			else:
de6d3b9:students/views.py:				#return none
de6d3b9:students/views.py:				#this shows all student as absent
de6d3b9:students/views.py:				attendance_object = None
de6d3b9:students/views.py:				attendance = None
de6d3b9:students/views.py:			
de6d3b9:students/views.py:	else:
de6d3b9:students/views.py:		#if no specific date is requested.
de6d3b9:students/views.py:		#show attendance for today.
de6d3b9:students/views.py:		try:
de6d3b9:students/views.py:			attendance_object = Attendance.objects.get(date=Date,Class=current_class)
de6d3b9:students/views.py:			attendance = attendance_object.present_students.all()
de6d3b9:students/views.py:		#if attendance does not exist
de6d3b9:students/views.py:		# assign attendance and object to none
de6d3b9:students/views.py:		#which makes all students absent in frontend
de6d3b9:students/views.py:		except Attendance.DoesNotExist:
de6d3b9:students/views.py:			attendance_object = None
de6d3b9:students/views.py:			attendance = None
de6d3b9:students/views.py:	
de6d3b9:students/views.py:	context={
de6d3b9:students/views.py:		'all_Info':all_Info,
de6d3b9:students/views.py:		'attendance': attendance,'all_students':request.user.teacher.teacher_class.student_set.all(),
de6d3b9:students/views.py:		'date':str(Date),
de6d3b9:students/views.py:		'type':type,
de6d3b9:students/views.py:	}
de6d3b9:students/views.py:	return render(request, 'students/attendance_page.html', context)
de6d3b9:students/views.py:	
de6d3b9:students/views.py:#ADD STUDENTS	
de6d3b9:students/views.py:@view_for("teacher")
de6d3b9:students/views.py:def update(request):
de6d3b9:students/views.py:	if request.method == 'POST':
de6d3b9:students/views.py:		#form to add new student
de6d3b9:students/views.py:		form = StudentForm(request.POST)
de6d3b9:students/views.py:		if form.is_valid():
de6d3b9:students/views.py:			#create object but dont save it
de6d3b9:students/views.py:			form = form.save(commit=False)
de6d3b9:students/views.py:			#assign student school
de6d3b9:students/views.py:			#assigns students school to teacher's school
de6d3b9:students/views.py:			teacher = request.user.teacher
de6d3b9:students/views.py:			form.school = teacher.teacher_class.school
de6d3b9:students/views.py:			#assigns students class to teacher's class
de6d3b9:students/views.py:			form.Class = teacher.teacher_class
de6d3b9:students/views.py:						
de6d3b9:students/views.py:			#Check get list of parents pks from post 
de6d3b9:students/views.py:			parents_list = request.POST.getlist("parents")
de6d3b9:students/views.py:			#Get first and second parent
de6d3b9:students/views.py:			f_parent = parents_list[0]
de6d3b9:students/views.py:			s_parent = parents_list[1]
de6d3b9:students/views.py:			# Check if f_parent and s_parent are not None
de6d3b9:students/views.py:			if f_parent or s_parent:
de6d3b9:students/views.py:			    #Initialize many to many list
de6d3b9:students/views.py:			    parent_list = []
de6d3b9:students/views.py:			    #Check if f_parent is not None, Validate username and user and add to many to many list
de6d3b9:students/views.py:			    if f_parent:
de6d3b9:students/views.py:			        try:
de6d3b9:students/views.py:			            parent = get_user_model().objects.get(username=f_parent).parent
de6d3b9:students/views.py:			            parent_list.append(parent.pk)
de6d3b9:students/views.py:			        except get_user_model().DoesNotExist:
de6d3b9:students/views.py:			            print("Does not exist")
de6d3b9:students/views.py:			            #UNF means user not found
de6d3b9:students/views.py:			            return HttpResponseServerError("UNF")
de6d3b9:students/views.py:			        except get_user_model().parent.RelatedObjectDoesNotExist:
de6d3b9:students/views.py:			            #UNP means user not parent
de6d3b9:students/views.py:			            print("Unp")
de6d3b9:students/views.py:			            return HttpResponseServerError("UNP")
de6d3b9:students/views.py:			   #Check if s_parent_parent is not None, Validate username and user and add to many to many list
de6d3b9:students/views.py:			    if s_parent:
de6d3b9:students/views.py:			        try:
de6d3b9:students/views.py:			            parent = get_user_model().objects.get(username=s_parent).parent
de6d3b9:students/views.py:			            parent_list.append(parent.pk)
de6d3b9:students/views.py:			        except get_user_model().DoesNotExist:
de6d3b9:students/views.py:			            print("Does not exist")
de6d3b9:students/views.py:			            #UNF means user not found
de6d3b9:students/views.py:			            return HttpResponseServerError("UNF")
de6d3b9:students/views.py:			        except get_user_model().parent.RelatedObjectDoesNotExist:
de6d3b9:students/views.py:			            #UNP means user not parent
de6d3b9:students/views.py:			            print("Unp")
de6d3b9:students/views.py:			            return HttpResponseServerError("UNP")
de6d3b9:students/views.py:			    #Save form and set parents
de6d3b9:students/views.py:			    form.save()
de6d3b9:students/views.py:			    form.parents.set(parent_list)
de6d3b9:students/views.py:			#If first parent and second parent are None create new parent.
de6d3b9:students/views.py:			else:
de6d3b9:students/views.py:				#form for creating parent
de6d3b9:students/views.py:				parentform = UserCreationForm(request.POST)
de6d3b9:students/views.py:			
de6d3b9:students/views.py:				if parentform.is_valid():
de6d3b9:students/views.py:					parentform = parentform.save(commit=False)
de6d3b9:students/views.py:					#create a schooluser for parent
de6d3b9:students/views.py:					parentform.level="Parent"
de6d3b9:students/views.py:					#save form
de6d3b9:students/views.py:					parentform.save()
de6d3b9:students/views.py:					#create parent object
de6d3b9:students/views.py:					parent = Parent(user=parentform)
de6d3b9:students/views.py:					#save parent object
de6d3b9:students/views.py:					parent.save()
de6d3b9:students/views.py:					form.save()
de6d3b9:students/views.py:					form.parents.add(parent)
de6d3b9:students/views.py:				else:
de6d3b9:students/views.py:					#if form is not valid return errors
de6d3b9:students/views.py:					return HttpResponseServerError(parentform.errors.as_json())
de6d3b9:students/views.py:			#if successful return this response
de6d3b9:students/views.py:			return HttpResponse('Success')
de6d3b9:students/views.py:		else:
de6d3b9:students/views.py:			return HttpResponseServerError(form.errors.as_data)
de6d3b9:students/views.py:	else:
de6d3b9:students/views.py:		#if request method is not post
de6d3b9:students/views.py:		#create student form and parent form
de6d3b9:students/views.py:		form = StudentForm()
de6d3b9:students/views.py:		parent_form = UserCreationForm()
de6d3b9:students/views.py:		#Remove fields first_name,last_name and email as they are not needed in the form
de6d3b9:students/views.py:		del parent_form.fields['first_name'],parent_form.fields['last_name'],parent_form.fields['email']
de6d3b9:students/views.py:		parent_form.use_required_attribute = False
de6d3b9:students/views.py:	return render(request,'students/update.html',{'form':form,"parent_form":parent_form,})
de6d3b9:students/views.py:	
de6d3b9:students/views.py:#update student and shows student edit form 
de6d3b9:students/views.py:@view_for("teacher")
de6d3b9:students/views.py:def update_students(request,pk):
de6d3b9:students/views.py:	#get student form of student by pk
de6d3b9:students/views.py:	form = StudentForm(instance=Student.objects.get(pk=pk))
de6d3b9:students/views.py:	student = Student.objects.get(pk=pk)
de6d3b9:students/views.py:	if request.method == "POST":
de6d3b9:students/views.py:		#get student form of student by pk
de6d3b9:students/views.py:		form = StudentForm(request.POST,instance=Student.objects.get(pk=pk))
de6d3b9:students/views.py:		if form.is_valid():
de6d3b9:students/views.py:			form = form.save(commit=False)
de6d3b9:students/views.py:			#Create empty list
de6d3b9:students/views.py:			parent_list = []
de6d3b9:students/views.py:			#Get first parent and second parents username
de6d3b9:students/views.py:			fparent = request.POST.get("fparent")
de6d3b9:students/views.py:			sparent = request.POST.get("sparent")
de6d3b9:students/views.py:			for n in (fparent,sparent):
de6d3b9:students/views.py:				#Where n = parent_username
de6d3b9:students/views.py:				#Check that n or  parent is not None, Validate username and user and add to many to many list
de6d3b9:students/views.py:				if n:
de6d3b9:students/views.py:					try:
de6d3b9:students/views.py:						parent = get_user_model().objects.get(username=n).parent
de6d3b9:students/views.py:						parent_list.append(parent.pk)
de6d3b9:students/views.py:					except get_user_model().DoesNotExist:
de6d3b9:students/views.py:						#UNF means user not found
de6d3b9:students/views.py:						return HttpResponseServerError("UNF")
de6d3b9:students/views.py:					except get_user_model().parent.RelatedObjectDoesNotExist:
de6d3b9:students/views.py:						#UNP means user not parent
de6d3b9:students/views.py:						return HttpResponseServerError("UNP")
de6d3b9:students/views.py:			#Save form and set parents
de6d3b9:students/views.py:			form.save()
de6d3b9:students/views.py:			form.parents.set(parent_list)
de6d3b9:students/views.py:			return HttpResponse("Success")
de6d3b9:students/views.py:		else:
de6d3b9:students/views.py:			return HttpResponseServerError("FORMERROR")
de6d3b9:students/views.py:	else:
de6d3b9:students/views.py:		#On get request
de6d3b9:students/views.py:		parents = student.parents.all()
de6d3b9:students/views.py:		#Get parents username to be shown in template
de6d3b9:students/views.py:		try:
de6d3b9:students/views.py:			fparent_username =  parents[0].user.get_username()
de6d3b9:students/views.py:		except IndexError:
de6d3b9:students/views.py:			fparent_username = ""
de6d3b9:students/views.py:		try:
de6d3b9:students/views.py:			sparent_username =  parents[1].user.get_username()
de6d3b9:students/views.py:		except IndexError:
de6d3b9:students/views.py:			sparent_username = ""
de6d3b9:students/views.py:		return render(request,"students/update_form.html",{"form":form,"fparent":fparent_username,"sparent":sparent_username,"student":student,})
de6d3b9:students/views.py:			
de6d3b9:students/views.py:#edit student view
de6d3b9:students/views.py:#shows edit students page
de6d3b9:students/views.py:#also deletes student
de6d3b9:students/views.py:#It shouldn't be like this i know.
de6d3b9:students/views.py:@view_for("teacher")
de6d3b9:students/views.py:def edit_students(request):
de6d3b9:students/views.py:	#can be used to delete students
de6d3b9:students/views.py:	#On post request delete student
de6d3b9:students/views.py:	if request.method == "POST":
de6d3b9:students/views.py:		student = get_object_or_404(Student, pk=int(request.POST.get("pk")),Class__teacher=request.user.teacher)
de6d3b9:students/views.py:		student.delete()
de6d3b9:students/views.py:		return HttpResponse(f"Student :  {student.name} was deleted successfully" )
de6d3b9:students/views.py:	else:
de6d3b9:students/views.py:		return render(request,"students/edit_students.html",{"all_students":request.user.teacher.teacher_class.student_set.all()
de6d3b9:students/views.py:})
de6d3b9:students/views.py:#View for creating and updating performance
de6d3b9:students/views.py:@view_for("teacher")
de6d3b9:students/views.py:def p_create_or_update(request, student_id):
de6d3b9:students/views.py:	try:
de6d3b9:students/views.py:		teacher =  request.user.teacher
de6d3b9:students/views.py:		#info variable represents student
de6d3b9:students/views.py:		info = Student.objects.get(Class__teacher=teacher,pk=student_id)
de6d3b9:students/views.py:		current_term = Term.objects.get(school=info.Class.school,current_session=True)
de6d3b9:students/views.py:		#get performance by subject
de6d3b9:students/views.py:		selected_subject = current_term.performance_set.filter(student=info).get(subject=request.POST['subject'])
de6d3b9:students/views.py:	except Term.DoesNotExist:
de6d3b9:students/views.py:		return HttpResponseServerError("SESSIONERROR")
de6d3b9:students/views.py:	except (Performance.DoesNotExist):
de6d3b9:students/views.py:		#if performance with added subject does not exist
de6d3b9:students/views.py:		#create new performance
de6d3b9:students/views.py:		selected_subject =info.performance_set.create(subject=request.POST['subject'], test=request.POST['test'], exam = request.POST['exam'],comment =request.POST['comment'],Class=request.user.teacher.teacher_class,term=current_term)
de6d3b9:students/views.py:		#return success message
de6d3b9:students/views.py:		return HttpResponse("Performance Added Successfully")
de6d3b9:students/views.py:	else:
de6d3b9:students/views.py:		#if performance with added subject exist.
de6d3b9:students/views.py:		#replace the added performance
de6d3b9:students/views.py:		selected_subject.test = request.POST['test']
de6d3b9:students/views.py:		selected_subject.exam = request.POST['exam']
de6d3b9:students/views.py:		selected_subject.comment = request.POST['comment']
de6d3b9:students/views.py:		selected_subject.save()
de6d3b9:students/views.py:		return HttpResponse(f'{selected_subject.subject} has been updated successfully')
de6d3b9:students/views.py:		
de6d3b9:students/views.py:#delete performance view
de6d3b9:students/views.py:@view_for("teacher")
de6d3b9:students/views.py:def delete(request):
de6d3b9:students/views.py:	if request.method == "POST":
de6d3b9:students/views.py:		#get performance then delete it
de6d3b9:students/views.py:		performance= get_object_or_404(Performance, pk=int(request.POST.get("pk")))
de6d3b9:students/views.py:		performance.delete()
de6d3b9:students/views.py:		return HttpResponse(f"Subject {performance.subject} was deleted successfully" )
de6d3b9:students/views.py:	
de6d3b9:students/views.py:#mark attendance view
de6d3b9:students/views.py:@view_for("teacher")
de6d3b9:students/views.py:def mark(request,Date):
de6d3b9:students/views.py:	if request.method == "POST":
de6d3b9:students/views.py:		print(request.POST)
de6d3b9:students/views.py:		#get list of present students
de6d3b9:students/views.py:		obj = request.POST.getlist('present')
de6d3b9:students/views.py:		#try to get attendance for requested date
de6d3b9:students/views.py:		try:
de6d3b9:students/views.py:			attendance=Attendance.objects.get(date=Date,Class=request.user.teacher.teacher_class)
de6d3b9:students/views.py:			#if attendance exist set the present students
de6d3b9:students/views.py:			attendance.present_students.set(obj)
de6d3b9:students/views.py:			attendance.save()
de6d3b9:students/views.py:			
de6d3b9:students/views.py:		except Attendance.DoesNotExist:
de6d3b9:students/views.py:			#if attendance does not exist
de6d3b9:students/views.py:			#create new attendance object
de6d3b9:students/views.py:			attendance=Attendance.objects.create(date=Date,Class=request.user.teacher.teacher_class)
de6d3b9:students/views.py:			attendance.present_students.set(obj)
de6d3b9:students/views.py:					
de6d3b9:students/views.py:		return HttpResponse("You Have Successfully added attendance for "+str(Date))
de6d3b9:students/views.py:	else:
de6d3b9:students/views.py:		return Http404
de6d3b9:students/views.py:#view for uploading student photo
de6d3b9:students/views.py:@view_for("teacher")
de6d3b9:students/views.py:def handle_uploads(request):
de6d3b9:students/views.py:	if request.method == "POST":
de6d3b9:students/views.py:		#Get photo fron request.FILES
de6d3b9:students/views.py:		file = request.FILES.get("photo")
de6d3b9:students/views.py:		#get student object
de6d3b9:students/views.py:		student = Student.objects.get(pk=request.POST.get("pk"))
de6d3b9:students/views.py:		#if photo is not default.jpg delete photo then save new one
de6d3b9:students/views.py:		if student.photo.name != "default.jpg":
de6d3b9:students/views.py:			student.photo.delete()
de6d3b9:students/views.py:		student.photo.save(file.name,file.file,save=True)		
de6d3b9:students/views.py:		return HttpResponse("Success")
de6d3b9:students/views.py:#View shows attendance in student profile
de6d3b9:students/views.py:@require_auth
de6d3b9:students/views.py:def view_only_attendance(request,pk):
de6d3b9:students/views.py:	user = request.user
de6d3b9:students/views.py:	#Get a student using primary key
de6d3b9:students/views.py:	level = user.level
de6d3b9:students/views.py:	if level == "Parent":
de6d3b9:students/views.py:		student =  user.parent.student_set.get(pk=pk)
de6d3b9:students/views.py:	elif level == "Admin":
de6d3b9:students/views.py:		student = Student.objects.get(Class__school__admin=user.admin,pk=pk)
de6d3b9:students/views.py:	else:
de6d3b9:students/views.py:		student = user.teacher.teacher_class.student_set.get(pk=pk)
de6d3b9:students/views.py:	#get attendance for the student class
de6d3b9:students/views.py:	attendance = student.Class.attendance_set.all()
de6d3b9:students/views.py:	#if date exists in request.Get
de6d3b9:students/views.py:	#this is for selecting showing particular dates
de6d3b9:students/views.py:	if "start_date" in request.GET.keys():
de6d3b9:students/views.py:		#try to get attendance for date requested
de6d3b9:students/views.py:		#convert date string to date object
de6d3b9:students/views.py:		start_date = request.GET.get("start_date")
de6d3b9:students/views.py:		end_date = request.GET.get("end_date")
de6d3b9:students/views.py:		#If requested_date is date in the future
de6d3b9:students/views.py:		if date.fromisoformat(start_date) > localdate():
de6d3b9:students/views.py:			return HttpResponse("DoesNotExist")
de6d3b9:students/views.py:		#Get attendance between date range
de6d3b9:students/views.py:		attendance = attendance.filter(date__range=(start_date,end_date))
de6d3b9:students/views.py:	else:
de6d3b9:students/views.py:		start_date = ""
de6d3b9:students/views.py:		end_date = ""
de6d3b9:students/views.py:	#Paginate attendance show only 7 days
de6d3b9:students/views.py:	paginator = Paginator(attendance,7)
de6d3b9:students/views.py:	attendance = paginator.get_page(request.GET.get("attendance_page"))
de6d3b9:students/views.py:	
de6d3b9:students/views.py:	return render(request,"students/view_only_attendance.html",{"attendance":attendance,"student":student,"start_date" : start_date,"end_date" : end_date})
de6d3b9:students/views.py:	
de6d3b9:students/views.py:#view shows performance in student profile
de6d3b9:students/views.py:@require_auth
de6d3b9:students/views.py:def view_only_performance(request,pk):
de6d3b9:students/views.py:	user = request.user
de6d3b9:students/views.py:	level = user.level
de6d3b9:students/views.py:	#Get student
de6d3b9:students/views.py:	if level == "Parent":
de6d3b9:students/views.py:		student =  user.parent.student_set.get(pk=pk)
de6d3b9:students/views.py:	elif level == "Admin":
de6d3b9:students/views.py:		student = Student.objects.get(Class__school__admin=user.admin,pk=pk)
de6d3b9:students/views.py:	else:
de6d3b9:students/views.py:		student = user.teacher.teacher_class.student_set.get(pk=pk)
de6d3b9:students/views.py:	term_html = None
de6d3b9:students/views.py:	#Parent argument exists if request is made by parent
de6d3b9:students/views.py:	#Check if parent is in get request keys
de6d3b9:students/views.py:	if "parent" in request.GET:
de6d3b9:students/views.py:		#Get all needed variables form term
de6d3b9:students/views.py:		terms=Term.objects.filter(school=student.Class.school)
de6d3b9:students/views.py:		try:
de6d3b9:students/views.py:			current_term = terms.get(current_session=True)
de6d3b9:students/views.py:		except Term.DoesNotExist:
de6d3b9:students/views.py:			return HttpResponseServerError("Sorry performances are not available for you to view yet")
de6d3b9:students/views.py:		year = current_term.year
de6d3b9:students/views.py:		term_text = current_term.term
de6d3b9:students/views.py:		#Render it in a template
de6d3b9:students/views.py:		data = '''<div>
de6d3b9:students/views.py:					<div class="d-flex flex-column">
de6d3b9:students/views.py:						<div class="d-flex">
de6d3b9:students/views.py:							<h6 class="w-50 ">Year</h6>
de6d3b9:students/views.py:							<h6 class="w-50">Term</h6>
de6d3b9:students/views.py:						</div>
de6d3b9:students/views.py:						<div class="d-flex my-2 mx-1"><select class="form-control" name="year"
de6d3b9:students/views.py:								id="year">
de6d3b9:students/views.py:								{% for term in terms %}
de6d3b9:students/views.py:								{% ifchanged %}<option value="{{term.year}}" {% if current_term.year == term.year %}selected{% endif %}>{{term.session}}</option>
de6d3b9:students/views.py:								{% endifchanged %}
de6d3b9:students/views.py:								{% endfor %}
de6d3b9:students/views.py:							</select>
de6d3b9:students/views.py:							<select class="ml-1 form-control" name="term" id="term">
de6d3b9:students/views.py:								<option {% if current_term.term == "1st Term"%}selected{% endif %}>1st Term</option>
de6d3b9:students/views.py:								<option {% if current_term.term == "2nd Term"%}selected{% endif %}>2nd Term</option>
de6d3b9:students/views.py:								<option {% if current_term.term == "3rd Term"%}selected{% endif %}>3rd Term</option>
de6d3b9:students/views.py:							</select>
de6d3b9:students/views.py:							<button class=" ml-2 btn btn-dark " id="fetch-termly-performance" onclick="fetch_termly_performance(this)"><span
de6d3b9:students/views.py:									class="fa fa-repeat"></span></button>
de6d3b9:students/views.py:						</div>
de6d3b9:students/views.py:					</div>
de6d3b9:students/views.py:				</div>
de6d3b9:students/views.py:			'''
de6d3b9:students/views.py:		#Assign term_html to template
de6d3b9:students/views.py:		term_html = Template(data).render(Context({"current_term":current_term,"terms":terms}))
de6d3b9:students/views.py:	else:
de6d3b9:students/views.py:		try:
de6d3b9:students/views.py:			year = int(request.GET.get("year"))
de6d3b9:students/views.py:			term_text = request.GET.get("term")
de6d3b9:students/views.py:		except ValueError:
de6d3b9:students/views.py:			return HttpResponseServerError("Invalid session detected.")
de6d3b9:students/views.py:	#try to get term object
de6d3b9:students/views.py:	try:
de6d3b9:students/views.py:		term = Term.objects.get(school=student.Class.school,year=year,term=term_text)
de6d3b9:students/views.py:	except Term.DoesNotExist:
de6d3b9:students/views.py:		return HttpResponse("DOE_ERROR")
de6d3b9:students/views.py:	filtered_performance = list(student.performance_set.filter(term=term))
de6d3b9:students/views.py:	#create new attribute called termly_performance
de6d3b9:students/views.py:	student.termly_performance = filtered_performance
de6d3b9:students/views.py:	#Pagination
de6d3b9:students/views.py:	performance = student.termly_performance
de6d3b9:students/views.py:	paginator = Paginator(performance,10)
de6d3b9:students/views.py:	performance = paginator.get_page(request.GET.get("page"))
de6d3b9:students/views.py:	return render(request,"students/view_only_performance.html",{"student":student,"performance":performance,"terms":Term.objects.filter(school=student.Class.school),"term_html":term_html})		
de6d3b9:students/views.py:	
de6d3b9:students/views.py:def link_callback(uri,rel):
de6d3b9:students/views.py:	sUrl = settings.STATIC_URL
de6d3b9:students/views.py:	sRoot = settings.STATIC_ROOT
de6d3b9:students/views.py:	mUrl = settings.MEDIA_URL
de6d3b9:students/views.py:	mRoot = settings.MEDIA_ROOT
de6d3b9:students/views.py:	if uri.startswith(mUrl):
de6d3b9:students/views.py:		path = os.path.join(mRoot,uri.replace(mUrl,""))
de6d3b9:students/views.py:	elif uri.startswith(sUrl):
de6d3b9:students/views.py:		path = os.path.join(sRoot,uri.replace(sUrl,""))
de6d3b9:students/views.py:	else:
de6d3b9:students/views.py:		return uri
de6d3b9:students/views.py:	if not os.path.isfile(path):
de6d3b9:students/views.py:		raise Exception(f"Uri must start with {sUrl} {mUrl}.")
de6d3b9:students/views.py:	else:
de6d3b9:students/views.py:		return path
de6d3b9:students/views.py:#View returns print attendance page
de6d3b9:students/views.py:@require_auth
de6d3b9:students/views.py:def print_attendance(request,pk,start_date=None,end_date=None):
de6d3b9:students/views.py:	user = request.user
de6d3b9:students/views.py:	level = user.level
de6d3b9:students/views.py:	if level == "Parent":
de6d3b9:students/views.py:		student =  user.parent.student_set.get(pk=pk)
de6d3b9:students/views.py:	elif level == "Admin":
de6d3b9:students/views.py:		student = Student.objects.get(Class__school__admin=user.admin,pk=pk)
de6d3b9:students/views.py:	else:
de6d3b9:students/views.py:		student = user.teacher.teacher_class.student_set.get(pk=pk)
de6d3b9:students/views.py:	if start_date and end_date:
de6d3b9:students/views.py:		attendance = student.Class.attendance_set.filter(date__range=(start_date,end_date))
de6d3b9:students/views.py:	else:
de6d3b9:students/views.py:		attendance = student.Class.attendance_set.all()
de6d3b9:students/views.py:	return render(request,"students/show_student_attendance.html",{"student":student,"attendance":attendance})
de6d3b9:students/views.py:#View returns print performance page
de6d3b9:students/views.py:@require_auth
de6d3b9:students/views.py:def print_performance(request,pk,year,term):
de6d3b9:students/views.py:	user = request.user
de6d3b9:students/views.py:	level = user.level
de6d3b9:students/views.py:	#Get student using the type of user
de6d3b9:students/views.py:	if level == "Parent":
de6d3b9:students/views.py:		student =  user.parent.student_set.get(pk=pk)
de6d3b9:students/views.py:	elif level == "Admin":
de6d3b9:students/views.py:		student = Student.objects.get(Class__school__admin=user.admin,pk=pk)
de6d3b9:students/views.py:	else:
de6d3b9:students/views.py:		student = user.teacher.teacher_class.student_set.get(pk=pk)
de6d3b9:students/views.py:	term = Term.objects.get(school=student.Class.school,year=year,term=term)
de6d3b9:students/views.py:	performance = term.performance_set.filter(student=student)
de6d3b9:students/views.py:	context = {'student':student,'performance':performance,"term":term}
de6d3b9:students/views.py:	return render(request,"students/show_student_performance.html",context)
de6d3b9:students/views.py:#View for rendering attendance as pdf using xhtml2pdf
de6d3b9:students/views.py:@require_auth
de6d3b9:students/views.py:def convert_attendance_to_pdf(request,pk,start_date=None,end_date=None):
de6d3b9:students/views.py:	#Template for pdf
de6d3b9:students/views.py:	template = get_template("students/show_student_attendance.html")
de6d3b9:students/views.py:	user = request.user
de6d3b9:students/views.py:	level = user.level
de6d3b9:students/views.py:	#Get student
de6d3b9:students/views.py:	if level == "Parent":
de6d3b9:students/views.py:		student =  user.parent.student_set.get(pk=pk)
de6d3b9:students/views.py:	elif level == "Admin":
de6d3b9:students/views.py:		student = Student.objects.get(Class__school__admin=user.admin,pk=pk)
de6d3b9:students/views.py:	else:
de6d3b9:students/views.py:		student = user.teacher.teacher_class.student_set.get(pk=pk)
de6d3b9:students/views.py:	#If start_date and end_date is not none, get attendance with range else get all attendance
de6d3b9:students/views.py:	if start_date and end_date:
de6d3b9:students/views.py:		attendance = student.Class.attendance_set.filter(date__range=(start_date,end_date))
de6d3b9:students/views.py:	else:
de6d3b9:students/views.py:		attendance = student.Class.attendance_set.all()
de6d3b9:students/views.py:	
de6d3b9:students/views.py:	context = {'pagesize':'A4','student':student,'attendance':attendance,}
de6d3b9:students/views.py:	response = HttpResponse(content_type="application/pdf")
de6d3b9:students/views.py:	response['Content-Disposition'] = 'attachment; filename="attendance.pdf"'
de6d3b9:students/views.py:	html = template.render(context)
de6d3b9:students/views.py:	pdf = pisa.CreatePDF(html,dest=response,link_callback=link_callback)
de6d3b9:students/views.py:	if pdf.err:
de6d3b9:students/views.py:		return HttpResponse("An Error Occurred")
de6d3b9:students/views.py:	return response
de6d3b9:students/views.py:		
de6d3b9:students/views.py:#View for rendering performance as pdf using xhtml2pdf
de6d3b9:students/views.py:@require_auth
de6d3b9:students/views.py:def convert_performance_to_pdf(request,pk,year,term):
de6d3b9:students/views.py:	#Template for pdf
de6d3b9:students/views.py:	template = get_template("students/show_student_performance.html")
de6d3b9:students/views.py:	user = request.user
de6d3b9:students/views.py:	level = user.level
de6d3b9:students/views.py:	#Get student
de6d3b9:students/views.py:	if level == "Parent":
de6d3b9:students/views.py:		student =  user.parent.student_set.get(pk=pk)
de6d3b9:students/views.py:	elif level == "Admin":
de6d3b9:students/views.py:		student = Student.objects.get(Class__school__admin=user.admin,pk=pk)
de6d3b9:students/views.py:	else:
de6d3b9:students/views.py:		student = user.teacher.teacher_class.student_set.get(pk=pk)
de6d3b9:students/views.py:	#Get term and get performance for the term
de6d3b9:students/views.py:	term = Term.objects.get(school=student.Class.school,year=year,term=term)
de6d3b9:students/views.py:	performance = term.performance_set.filter(student=student)
de6d3b9:students/views.py:	context = {'pagesize':'A4','student':student,'performance':performance,"term":term}
de6d3b9:students/views.py:	response = HttpResponse(content_type="application/pdf")
de6d3b9:students/views.py:	response['Content-Disposition'] = 'attachment; filename="performance.pdf"'
de6d3b9:students/views.py:	html = template.render(context)
de6d3b9:students/views.py:	pdf = pisa.CreatePDF(html,dest=response,link_callback=link_callback)
de6d3b9:students/views.py:	if pdf.err:
de6d3b9:students/views.py:		return HttpResponse("An Error Occurred")
de6d3b9:students/views.py:	return response
de6d3b9:students/views.py:	
de6d3b9:students/views.py:#Handles performance csv_handler
de6d3b9:students/views.py:@view_for("teacher")
de6d3b9:students/views.py:def csv_handler(request):
de6d3b9:students/views.py:	if request.method == "POST":
de6d3b9:students/views.py:		#Get neccessary data
de6d3b9:students/views.py:		teacher = request.user.teacher
de6d3b9:students/views.py:		current_class = teacher.teacher_class
de6d3b9:students/views.py:		student = Student.objects.get(Class=current_class,pk=request.POST.get("student_pk"))
de6d3b9:students/views.py:		#Get school current term
de6d3b9:students/views.py:		term = Term.objects.get(school=current_class.school,current_session=True)
de6d3b9:students/views.py:		csv_file = request.FILES["csv_file"]
de6d3b9:students/views.py:		#Check if uploaded file is greater than 100kb
de6d3b9:students/views.py:		if csv_file.size > 100000:
de6d3b9:students/views.py:			#Return file too big message
de6d3b9:students/views.py:			return HttpResponse("File size too large")
de6d3b9:students/views.py:		#Read csv file
de6d3b9:students/views.py:		csv_file = csv_file.read()
de6d3b9:students/views.py:		#Convert from bytes to string and splitlines to enable csvreader to read
de6d3b9:students/views.py:		csv_file = csv_file.decode("utf-8").splitlines()
de6d3b9:students/views.py:		#Sometimes csv file may come with \ufeff char
de6d3b9:students/views.py:		#Strip that character from first list index
de6d3b9:students/views.py:		csv_file[0] = csv_file[0].lstrip("\ufeff")
de6d3b9:students/views.py:		#Csv reader
de6d3b9:students/views.py:		csv_reader = csv.DictReader(csv_file)
de6d3b9:students/views.py:		#Line count var to count number of lines
de6d3b9:students/views.py:		line_count = 0
de6d3b9:students/views.py:		for row in csv_reader:
de6d3b9:students/views.py:			#Try to get performance if it exists or create new one
de6d3b9:students/views.py:			try:
de6d3b9:students/views.py:				performance = term.performance_set.get(subject=row["subject"],student=student)
de6d3b9:students/views.py:				performance.test = row["test_score"]
de6d3b9:students/views.py:				performance.exam = row["exam_score"]
de6d3b9:students/views.py:				performance.comment = row["comment"]
de6d3b9:students/views.py:				performance.save()
de6d3b9:students/views.py:			except:
de6d3b9:students/views.py:				performance = Performance.objects.create(term=term,Class=current_class,student=student,subject=row["subject"],test=row["test_score"],exam=row["exam_score"],comment=row["comment"])
de6d3b9:students/views.py:			line_count+=1
de6d3b9:students/views.py:		#Return success message with number of performances added(line_count-1 because the first line is not counted)
de6d3b9:students/views.py:		return HttpResponse(f"{line_count} performances for {student.name} added successfully.")
de6d3b9:students/views.py:	else:
de6d3b9:students/views.py:		response = HttpResponse(content_type="text/csv")
de6d3b9:students/views.py:		response['Content-Disposition'] = 'attachment; filename="template.csv"'
de6d3b9:students/views.py:		writer = csv.writer(response)
de6d3b9:students/views.py:		writer.writerow(['subject','test_score','exam_score','comment'])
de6d3b9:students/views.py:		return response
de6d3b9:students/views.py:	
