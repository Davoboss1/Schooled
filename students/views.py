import os
import csv
from django.shortcuts import render,redirect,get_object_or_404,Http404,HttpResponse,reverse
from django.http.response import HttpResponseServerError
from .models import Student, Performance, Attendance,Term
from teachers.models import Teacher
from admins.models import Admin
from admins.views import loadmore_performance
from parents.models import Parent
from django.db.models import Q
from accounts.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .forms  import StudentForm, PerformanceForm
from django.contrib import messages
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from django.template.loader import render_to_string,get_template
from django.template import Context,Template
from datetime import datetime,date,timedelta
from django.utils.timezone import localdate
from django.core.paginator import Paginator
from xhtml2pdf import pisa
from io import StringIO
from schooled import settings
from tools import view_for,require_ajax,require_auth
#FUNCTION BASED VIEWS

#View for viewing performance
#Used by teachers
@view_for("teacher")
@require_ajax
def performance_page(request,type):
	school = request.user.teacher.teacher_class.school
	context={
		'type':type,
		"terms":Term.objects.filter(school=school),
		'current_term':Term.objects.filter(school=school,current_session=True).first()
	}
	#Pagination of students
	if "page" in request.GET.keys():
		#get all students in teachers class
		all_Info= request.user.teacher.teacher_class.student_set.all()
		
		#Paginate students, Show only 10 objects
		paginator = Paginator(all_Info,10)
		all_Info = paginator.get_page(request.GET.get("page"))
		#assign variables to context
		context["all_Info"] = all_Info
		#If type of request is edit-performance just render edit-performance template
		if type == "edit-performance":
			teacher_class = request.user.teacher.teacher_class
			available_subjects = teacher_class.performance_set.only("subject").values_list('subject',flat=True).distinct()
			context["available_subjects"] = available_subjects
			return render(request,"students/pagination/edit-performance.html",context)
		else:
			context['url'] = reverse("students:performance_page",kwargs={"type":"view-performance"})
			#get year and term value
			if "year" in request.GET.keys() and "term" in request.GET.keys():
				#try to get term object
				try:
					year = int(request.GET.get("year"))
					term_text = request.GET.get("term")
					term = Term.objects.get(year=year,term=term_text,school=school)
				except Term.DoesNotExist:
					return HttpResponse("DOE_ERROR")
				except ValueError:
					return HttpResponseServerError("Invalid session detected")
				#get all students in the paginated object list
				for student in all_Info.object_list:
					#filter the performance by term
					filtered_performance = list(student.performance_set.filter(term=term))
					#create new attribute called termly_performance
					student.termly_performance = filtered_performance			
			return render(request,"students/pagination/performance_page.html",context)
	#If performance for particular student
	#Mainly for loading more performances
	if "student_pk" in request.GET.keys():
		student = Student.objects.get(pk=int(request.GET.get("student_pk")))
		year = int(request.GET.get("year"))
		term_text = request.GET.get("term")
		#try to get term object
		term = Term.objects.get(year=year,term=term_text,school=school)
		filtered_performance = list(student.performance_set.filter(term=term))
		#create new attribute called termly_performance
		student.termly_performance = filtered_performance
		return HttpResponse(loadmore_performance(student.termly_performance,10,int(request.GET.get("page_no"))))
	context["students"] = request.user.teacher.teacher_class.student_set.all()
	return render(request, 'students/performance_page.html', context)



#Function for STUDENTS ATTENDANCE
@view_for("teacher")
@require_ajax
def attendance_page(request,type):
	#get all student in in teachers class
	all_Info= request.user.teacher.teacher_class.student_set.all()
	current_class = request.user.teacher.teacher_class
	Date =localdate()


	#if a particular date is requested
	if "date" in request.GET.keys():
		#get requested date
		Date = request.GET.get("date")
		#try to get attendance by date and class
		try:
			attendance_object = Attendance.objects.get(date=Date,Class=current_class)
			attendance = attendance_object.present_students.all()
			
		#if attendance does'nt exist
		except Attendance.DoesNotExist:
		
			date_list = Date.split("-")
			Date = date(int(date_list[0]),int(date_list[1]),int(date_list[2]))
			#if date is in future
			if Date > localdate():
				return HttpResponseServerError('<div class="alert alert-danger alert-dismissible fade show" role="alert"><strong>Oops! sorry</strong> You can\'t add or view date for the future .<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>')
			else:
				#return none
				#this shows all student as absent
				attendance_object = None
				attendance = None
			
	else:
		#if no specific date is requested.
		#show attendance for today.
		try:
			attendance_object = Attendance.objects.get(date=Date,Class=current_class)
			attendance = attendance_object.present_students.all()
		#if attendance does not exist
		# assign attendance and object to none
		#which makes all students absent in frontend
		except Attendance.DoesNotExist:
			attendance_object = None
			attendance = None
	
	context={
		'all_Info':all_Info,
		'attendance': attendance,'all_students':request.user.teacher.teacher_class.student_set.all(),
		'date':str(Date),
		'type':type,
	}
	return render(request, 'students/attendance_page.html', context)
	

#ADD STUDENTS	
@view_for("teacher")
@require_ajax
def update(request):
	if request.method == 'POST':
		#form to add new student
		form = StudentForm(request.POST)
		if form.is_valid():
			#create object but dont save it
			form = form.save(commit=False)
			#assign student school
			#assigns students school to teacher's school
			teacher = request.user.teacher
			form.school = teacher.teacher_class.school
			#assigns students class to teacher's class
			form.Class = teacher.teacher_class
						
			#Check get list of parents pks from post 
			parents_list = request.POST.getlist("parents")
			#Get first and second parent
			f_parent = parents_list[0]
			s_parent = parents_list[1]
			# Check if f_parent and s_parent are not None
			if f_parent or s_parent:
			    #Initialize many to many list
			    parent_list = []
			    #Check if f_parent is not None, Validate username and user and add to many to many list
			    if f_parent:
			        try:
			            parent = get_user_model().objects.get(username=f_parent).parent
			            parent_list.append(parent.pk)
			        except get_user_model().DoesNotExist:
			            print("Does not exist")
			            #UNF means user not found
			            return HttpResponseServerError("UNF")
			        except get_user_model().parent.RelatedObjectDoesNotExist:
			            #UNP means user not parent
			            print("Unp")
			            return HttpResponseServerError("UNP")
			   #Check if s_parent_parent is not None, Validate username and user and add to many to many list
			    if s_parent:
			        try:
			            parent = get_user_model().objects.get(username=s_parent).parent
			            parent_list.append(parent.pk)
			        except get_user_model().DoesNotExist:
			            print("Does not exist")
			            #UNF means user not found
			            return HttpResponseServerError("UNF")
			        except get_user_model().parent.RelatedObjectDoesNotExist:
			            #UNP means user not parent
			            print("Unp")
			            return HttpResponseServerError("UNP")
			    #Save form and set parents
			    form.save()
			    form.parents.set(parent_list)
			#If first parent and second parent are None create new parent.
			else:
				#form for creating parent
				parentform = UserCreationForm(request.POST)
			
				if parentform.is_valid():
					parentform = parentform.save(commit=False)
					#create a schooluser for parent
					parentform.level="Parent"
					#save form
					parentform.save()
					#create parent object
					parent = Parent(user=parentform)
					#save parent object
					parent.save()
					form.save()
					form.parents.add(parent)
				else:
					#if form is not valid return errors
					return HttpResponseServerError(parentform.errors.as_json())
			#if successful return this response
			return HttpResponse('Success')
		else:
			return HttpResponseServerError(form.errors.as_data)
	else:
		#if request method is not post
		#create student form and parent form
		form = StudentForm()
		parent_form = UserCreationForm()
		#Remove fields first_name,last_name and email as they are not needed in the form
		del parent_form.fields['first_name'],parent_form.fields['last_name'],parent_form.fields['email']

		parent_form.use_required_attribute = False
	return render(request,'students/update.html',{'form':form,"parent_form":parent_form,})
	
#update student and shows student edit form 
@view_for("teacher")
@require_ajax
def update_students(request,pk):
	#get student form of student by pk
	form = StudentForm(instance=Student.objects.get(pk=pk))
	student = Student.objects.get(pk=pk)
	if request.method == "POST":
		#get student form of student by pk
		form = StudentForm(request.POST,instance=Student.objects.get(pk=pk))
		if form.is_valid():
			form = form.save(commit=False)
			#Create empty list
			parent_list = []
			#Get first parent and second parents username
			fparent = request.POST.get("fparent")
			sparent = request.POST.get("sparent")
			for n in (fparent,sparent):
				#Where n = parent_username
				#Check that n or  parent is not None, Validate username and user and add to many to many list
				if n:
					try:
						parent = get_user_model().objects.get(username=n).parent
						parent_list.append(parent.pk)
					except get_user_model().DoesNotExist:
						#UNF means user not found
						return HttpResponseServerError("UNF")
					except get_user_model().parent.RelatedObjectDoesNotExist:
						#UNP means user not parent
						return HttpResponseServerError("UNP")
			#Save form and set parents
			form.save()
			form.parents.set(parent_list)
			return HttpResponse("Success")
		else:
			return HttpResponseServerError("FORMERROR")
	else:
		#On get request
		parents = student.parents.all()
		#Get parents username to be shown in template
		try:
			fparent_username =  parents[0].user.get_username()
		except IndexError:
			fparent_username = ""
		try:
			sparent_username =  parents[1].user.get_username()
		except IndexError:
			sparent_username = ""

		return render(request,"students/update_form.html",{"form":form,"fparent":fparent_username,"sparent":sparent_username,"student":student,})
			
#edit student view
#shows edit students page
#also deletes student
#It shouldn't be like this i know.
@view_for("teacher")
@require_ajax
def edit_students(request):
	#can be used to delete students
	#On post request delete student
	if request.method == "POST":
		student = get_object_or_404(Student, pk=int(request.POST.get("pk")),Class__teacher=request.user.teacher)
		student.delete()
		return HttpResponse(f"Student :  {student.name} was deleted successfully" )
	else:
		return render(request,"students/edit_students.html",{"all_students":request.user.teacher.teacher_class.student_set.all()
})

#View for creating and updating performance
@view_for("teacher")
@require_ajax
def p_create_or_update(request, student_id):
	try:
		teacher =  request.user.teacher
		#info variable represents student
		info = Student.objects.get(Class__teacher=teacher,pk=student_id)
		current_term = Term.objects.get(school=info.Class.school,current_session=True)
		#get performance by subject
		selected_subject = current_term.performance_set.filter(student=info).get(subject=request.POST['subject'])
	except Term.DoesNotExist:
		return HttpResponseServerError("SESSIONERROR")
	except (Performance.DoesNotExist):
		#if performance with added subject does not exist
		#create new performance
		selected_subject =info.performance_set.create(subject=request.POST['subject'], test=request.POST['test'], exam = request.POST['exam'],comment =request.POST['comment'],Class=request.user.teacher.teacher_class,term=current_term)
		#return success message
		return HttpResponse("Performance Added Successfully")
	else:
		#if performance with added subject exist.
		#replace the added performance
		selected_subject.test = request.POST['test']
		selected_subject.exam = request.POST['exam']
		selected_subject.comment = request.POST['comment']
		selected_subject.save()
		return HttpResponse(f'{selected_subject.subject} has been updated successfully')
		
#delete performance view
@view_for("teacher")
@require_ajax
def delete(request):
	if request.is_ajax():
		if request.method == "POST":
			#get performance then delete it
			performance= get_object_or_404(Performance, pk=int(request.POST.get("pk")))
			performance.delete()
			return HttpResponse(f"Subject {performance.subject} was deleted successfully" )
	
#mark attendance view
@view_for("teacher")
@require_ajax
def mark(request,Date):
	if request.method == "POST":
		print(request.POST)
		#get list of present students
		obj = request.POST.getlist('present')
		#try to get attendance for requested date
		try:
			attendance=Attendance.objects.get(date=Date,Class=request.user.teacher.teacher_class)
			#if attendance exist set the present students
			attendance.present_students.set(obj)
			attendance.save()
			
		except Attendance.DoesNotExist:
			#if attendance does not exist
			#create new attendance object
			attendance=Attendance.objects.create(date=Date,Class=request.user.teacher.teacher_class)
			attendance.present_students.set(obj)
					
		return HttpResponse("You Have Successfully added attendance for "+str(Date))
	else:
		return Http404

#view for uploading student photo
@view_for("teacher")
@require_ajax
def handle_uploads(request):
	if request.method == "POST":
		#Get photo fron request.FILES
		file = request.FILES.get("photo")
		#get student object
		student = Student.objects.get(pk=request.POST.get("pk"))
		#if photo is not default.jpg delete photo then save new one
		if student.photo.name != "default.jpg":
			student.photo.delete()
		student.photo.save(file.name,file.file,save=True)		
		return HttpResponse("Success")

#View shows attendance in student profile
@require_auth
def view_only_attendance(request,pk):
	user = request.user
	#Get a student using primary key
	level = user.level
	if level == "Parent":
		student =  user.parent.student_set.get(pk=pk)
	elif level == "Admin":
		student = Student.objects.get(Class__school__admin=user.admin,pk=pk)
	else:
		student = user.teacher.teacher_class.student_set.get(pk=pk)
	#get attendance for the student class
	attendance = student.Class.attendance_set.all()
	#if date exists in request.Get
	#this is for selecting showing particular dates
	if "start_date" in request.GET.keys():
		#try to get attendance for date requested
		#convert date string to date object

		start_date = request.GET.get("start_date")
		end_date = request.GET.get("end_date")
		#If requested_date is date in the future
		if date.fromisoformat(start_date) > localdate():
			return HttpResponse("DoesNotExist")
		#Get attendance between date range
		attendance = attendance.filter(date__range=(start_date,end_date))
	else:
		start_date = ""
		end_date = ""

	#Paginate attendance show only 7 days
	paginator = Paginator(attendance,7)
	attendance = paginator.get_page(request.GET.get("attendance_page"))
	
	return render(request,"students/view_only_attendance.html",{"attendance":attendance,"student":student,"start_date" : start_date,"end_date" : end_date})
	
#view shows performance in student profile
@require_auth
def view_only_performance(request,pk):
	user = request.user
	level = user.level
	#Get student
	if level == "Parent":
		student =  user.parent.student_set.get(pk=pk)
	elif level == "Admin":
		student = Student.objects.get(Class__school__admin=user.admin,pk=pk)
	else:
		student = user.teacher.teacher_class.student_set.get(pk=pk)
	term_html = None
	#Parent argument exists if request is made by parent
	#Check if parent is in get request keys
	if "parent" in request.GET:
		#Get all needed variables form term
		terms=Term.objects.filter(school=student.Class.school)
		try:
			current_term = terms.get(current_session=True)
		except Term.DoesNotExist:
			return HttpResponseServerError("Sorry performances are not available for you to view yet")
		year = current_term.year
		term_text = current_term.term
		#Render it in a template
		data = '''<div>
					<div class="d-flex flex-column">
						<div class="d-flex">
							<h6 class="w-50 ">Year</h6>
							<h6 class="w-50">Term</h6>
						</div>
						<div class="d-flex my-2 mx-1"><select class="form-control" name="year"
								id="year">
								{% for term in terms %}
								{% ifchanged %}<option value="{{term.year}}" {% if current_term.year == term.year %}selected{% endif %}>{{term.session}}</option>
								{% endifchanged %}
								{% endfor %}
							</select>
							<select class="ml-1 form-control" name="term" id="term">
								<option {% if current_term.term == "1st Term"%}selected{% endif %}>1st Term</option>
								<option {% if current_term.term == "2nd Term"%}selected{% endif %}>2nd Term</option>
								<option {% if current_term.term == "3rd Term"%}selected{% endif %}>3rd Term</option>
							</select>
							<button class=" ml-2 btn btn-dark " id="fetch-termly-performance" onclick="fetch_termly_performance(this)"><span
									class="fa fa-repeat"></span></button>
						</div>
					</div>
				</div>
			'''
		#Assign term_html to template
		term_html = Template(data).render(Context({"current_term":current_term,"terms":terms}))
	else:
		try:
			year = int(request.GET.get("year"))
			term_text = request.GET.get("term")
		except ValueError:
			return HttpResponseServerError("Invalid session detected.")

	#try to get term object
	try:
		term = Term.objects.get(school=student.Class.school,year=year,term=term_text)
	except Term.DoesNotExist:
		return HttpResponse("DOE_ERROR")
	filtered_performance = list(student.performance_set.filter(term=term))
	#create new attribute called termly_performance
	student.termly_performance = filtered_performance
	#Pagination
	performance = student.termly_performance
	paginator = Paginator(performance,10)
	performance = paginator.get_page(request.GET.get("page"))
	return render(request,"students/view_only_performance.html",{"student":student,"performance":performance,"terms":Term.objects.filter(school=student.Class.school),"term_html":term_html})		
	
def link_callback(uri,rel):
	sUrl = settings.STATIC_URL
	sRoot = settings.STATIC_ROOT
	mUrl = settings.MEDIA_URL
	mRoot = settings.MEDIA_ROOT
	if uri.startswith(mUrl):
		path = os.path.join(mRoot,uri.replace(mUrl,""))
	elif uri.startswith(sUrl):
		path = os.path.join(sRoot,uri.replace(sUrl,""))
	else:
		return uri
	if not os.path.isfile(path):
		raise Exception(f"Uri must start with {sUrl} {mUrl}.")
	else:
		return path

#View returns print attendance page
@require_auth
def print_attendance(request,pk,start_date=None,end_date=None):
	user = request.user
	level = user.level
	if level == "Parent":
		student =  user.parent.student_set.get(pk=pk)
	elif level == "Admin":
		student = Student.objects.get(Class__school__admin=user.admin,pk=pk)
	else:
		student = user.teacher.teacher_class.student_set.get(pk=pk)
	if start_date and end_date:
		attendance = student.Class.attendance_set.filter(date__range=(start_date,end_date))
	else:
		attendance = student.Class.attendance_set.all()
	return render(request,"students/show_student_attendance.html",{"student":student,"attendance":attendance})
#View returns print performance page
@require_auth
def print_performance(request,pk,year,term):
	user = request.user
	level = user.level
	#Get student using the type of user
	if level == "Parent":
		student =  user.parent.student_set.get(pk=pk)
	elif level == "Admin":
		student = Student.objects.get(Class__school__admin=user.admin,pk=pk)
	else:
		student = user.teacher.teacher_class.student_set.get(pk=pk)
	term = Term.objects.get(school=student.Class.school,year=year,term=term)
	performance = term.performance_set.filter(student=student)
	context = {'student':student,'performance':performance,"term":term}

	return render(request,"students/show_student_performance.html",context)

#View for rendering attendance as pdf using xhtml2pdf
@require_auth
def convert_attendance_to_pdf(request,pk,start_date=None,end_date=None):
	#Template for pdf
	template = get_template("students/show_student_attendance.html")
	user = request.user
	level = user.level
	#Get student
	if level == "Parent":
		student =  user.parent.student_set.get(pk=pk)
	elif level == "Admin":
		student = Student.objects.get(Class__school__admin=user.admin,pk=pk)
	else:
		student = user.teacher.teacher_class.student_set.get(pk=pk)
	#If start_date and end_date is not none, get attendance with range else get all attendance
	if start_date and end_date:
		attendance = student.Class.attendance_set.filter(date__range=(start_date,end_date))
	else:
		attendance = student.Class.attendance_set.all()
	
	context = {'pagesize':'A4','student':student,'attendance':attendance,}
	response = HttpResponse(content_type="application/pdf")
	response['Content-Disposition'] = 'attachment; filename="attendance.pdf"'
	html = template.render(context)
	pdf = pisa.CreatePDF(html,dest=response,link_callback=link_callback)
	if pdf.err:
		return HttpResponse("An Error Occurred")
	return response
		
#View for rendering performance as pdf using xhtml2pdf
@require_auth
def convert_performance_to_pdf(request,pk,year,term):
	#Template for pdf
	template = get_template("students/show_student_performance.html")
	user = request.user
	level = user.level
	#Get student
	if level == "Parent":
		student =  user.parent.student_set.get(pk=pk)
	elif level == "Admin":
		student = Student.objects.get(Class__school__admin=user.admin,pk=pk)
	else:
		student = user.teacher.teacher_class.student_set.get(pk=pk)
	#Get term and get performance for the term
	term = Term.objects.get(school=student.Class.school,year=year,term=term)
	performance = term.performance_set.filter(student=student)

	context = {'pagesize':'A4','student':student,'performance':performance,"term":term}
	response = HttpResponse(content_type="application/pdf")
	response['Content-Disposition'] = 'attachment; filename="performance.pdf"'
	html = template.render(context)
	pdf = pisa.CreatePDF(html,dest=response,link_callback=link_callback)
	if pdf.err:
		return HttpResponse("An Error Occurred")
	return response
	

#Handles performance csv_handler
@view_for("teacher")
def csv_handler(request):
	if request.method == "POST":
		#Get neccessary data
		teacher = request.user.teacher
		current_class = teacher.teacher_class
		student = Student.objects.get(Class=current_class,pk=request.POST.get("student_pk"))
		#Get school current term
		term = Term.objects.get(school=current_class.school,current_session=True)
		csv_file = request.FILES["csv_file"]
		#Check if uploaded file is greater than 100kb
		if csv_file.size > 100000:
			#Return file too big message
			return HttpResponse("File size too large")
		#Read csv file
		csv_file = csv_file.read()
		#Convert from bytes to string and splitlines to enable csvreader to read
		csv_file = csv_file.decode("utf-8").splitlines()
		#Sometimes csv file may come with \ufeff char
		#Strip that character from first list index
		csv_file[0] = csv_file[0].lstrip("\ufeff")
		#Csv reader
		csv_reader = csv.DictReader(csv_file)
		#Line count var to count number of lines
		line_count = 0
		for row in csv_reader:
			#Try to get performance if it exists or create new one
			try:
				performance = term.performance_set.get(subject=row["subject"],student=student)
				performance.test = row["test_score"]
				performance.exam = row["exam_score"]
				performance.comment = row["comment"]
				performance.save()
			except:
				performance = Performance.objects.create(term=term,Class=current_class,student=student,subject=row["subject"],test=row["test_score"],exam=row["exam_score"],comment=row["comment"])

			line_count+=1
		#Return success message with number of performances added(line_count-1 because the first line is not counted)
		return HttpResponse(f"{line_count} performances for {student.name} added successfully.")
	else:
		response = HttpResponse(content_type="text/csv")
		response['Content-Disposition'] = 'attachment; filename="template.csv"'
		writer = csv.writer(response)
		writer.writerow(['subject','test_score','exam_score','comment'])
		return response
	

