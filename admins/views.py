from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import check_password
from .forms import SchoolForm, AdminForm
from teachers.models import Class, Teacher
from teachers.forms import TeacherForm
from .models import Admin, School
from accounts.forms import UserCreationForm, UserUpdateForm
from django.template.loader import render_to_string
from django.template import Template, Context
from django.http.response import HttpResponse, HttpResponseNotFound, HttpResponseServerError, JsonResponse
from django.urls import reverse
from students.models import Student, Attendance, Term
from django.core.paginator import Paginator, EmptyPage
from django.http.response import Http404, HttpResponseServerError
from django.core.exceptions import ValidationError
from django.db.models import Q
from tools import require_ajax, view_for, save_picture, require_auth, render_alert
from students.models import School_activity_log
from accounts.models import Messages

# Create your views here.
# Writes from error in string of h6 tags


def get_errors_in_text(form):
    errors_dict = form.errors.as_data()
    error_text = ""
    for keys in errors_dict.keys():
        error_text += f"<h6 class='py-2 text-center' > {errors_dict[keys][0].messages[0]} </h6>"
    return error_text

# school_owner or admin homepage


@view_for("admin")
def school_owner_home_page(request):
    user = request.user
    # Gets user unread messages
    unread_msg_count = Messages.objects.filter(Q(conversation__reciever=user) | Q(
        conversation__sender=user.get_username()), message_read=False).exclude(sent_by=user.get_username()).count()

    # Gets all user schools
    schools = request.user.admin.schools.all()
    # Gets all schools unread notifications number at set it to a new attribute notif_count
    for school in schools:
        school.notif_count = School_activity_log.objects.filter(
            Class__school=school, viewed=False).count()

    # School form for creating new form
    sch_form = SchoolForm()
    # Default notif_count to be shown.
    # Gets notif_count of first school
    if schools.exists():
        notif_count = schools[0].notif_count
    else:
        notif_count = 0
    new_user = request.session.get(user.username + "_new_user")
    if new_user:
        del request.session[user.username+"_new_user"]
    return render(request, "admins/school_owner_admin_page.html", {'user': request.user, "unread_msg_count": unread_msg_count, "unviewed_notifications_count": notif_count, "schoolform": sch_form, "schools": schools, "new_user": new_user})


# View for creating a new school
@view_for("admin")
def create_new_school(request):
    sch_form = SchoolForm(request.POST)
    if sch_form.is_valid():
        sch = sch_form.save(commit=False)
        # Get admin object and set it as the admin of newly create school
        admin = request.user.admin
        sch.admin = admin
        sch.save()
        save_picture(sch.image, request.FILES.get("school-image"))
        return JsonResponse({"name": sch.school_name, "pk": sch.pk, "motto": sch.motto})
    else:
        return HttpResponseServerError(get_errors_in_text(sch_form))

# Delete school view (Obvi)


@view_for("admin")
def delete_school(request):
    # Get password and verify if its user correct password
    password = request.POST.get("password")
    valid_password = check_password(password, request.user.password)
    if valid_password:
        # If valid password.
        # Get school by admin and pk and delete it.
        sch_pk = request.POST.get("sch_pk")
        School.objects.get(admin=request.user.admin, pk=sch_pk).delete()
        return HttpResponse("Deleted successfully")
    else:
        # return server error
        # WP = Wrong Password
        return HttpResponseServerError("WP")

# This view does three things.
# Views school and admin information from admin page.
# Changes school information.
# Changes admin information.
# Changes admin password.
# Basically it performs all functions on the school profile page


@view_for("admin")
def school_profile(request, sch_pk):
    current_user = request.user
    admin = current_user.admin
    school = admin.schools.get(pk=sch_pk)
    if request.method == "POST":
        # fortype contains type of action to be performed.
        formtype = request.POST.get("formtype")
        if formtype == "school":
            # Updates school information
            form = SchoolForm(request.POST, instance=school)
            if form.is_valid():
                form = form.save()
                save_picture(form.image, request.FILES.get("sch-logo"))
                return HttpResponse(render_alert("School has been updated successfully"))
            else:
                # Returns form erros
                return HttpResponseServerError(get_errors_in_text(form))
        elif formtype == "admin":
            # Updates admin and user information
            form = UserUpdateForm(request.POST, instance=current_user)
            admin_form = AdminForm(request.POST, instance=current_user.admin)
            if form.is_valid() and admin_form.is_valid():
                form = form.save()
                # for handling profile picture upload
                save_picture(form.profile_picture,
                             request.FILES.get("user-profile-picture"))
                admin_form.save()
                return HttpResponse(render_alert("Admin has been updated successfully"))

            else:
                return HttpResponseServerError(get_errors_in_text(form) + get_errors_in_text(admin_form))
        elif formtype == "password":
            # Changes password
            # Updates password with password change form
            form = PasswordChangeForm(current_user, request.POST)
            if form.is_valid():
                form.save()
                return HttpResponse(render_alert("Password has been changed successfully"))

            else:
                return HttpResponseServerError(get_errors_in_text(form))
    # This checks get request for formtype and renders type of form requested.
    # I.e : if type is school return page with school form.

    if request.GET.get("type") == "school":
        return render(request, "admins/update-school-and-admin.html", {"form": SchoolForm(instance=school), "type": "school", },)
    elif request.GET.get("type") == "admin":
        return render(request, "admins/update-school-and-admin.html", {"form": AdminForm(instance=current_user.admin), "userform": UserUpdateForm(instance=current_user), "type": "admin", })
    elif request.GET.get("type") == "password":
        return render(request, "admins/update-school-and-admin.html", {"form": PasswordChangeForm(current_user), "type": "password", },)

    students_no = Student.objects.filter(Class__school=school).count()
    teachers_no = Teacher.objects.filter(teacher_class__school=school).count()

    return render(request, "admins/school_profile.html", {'user': current_user, "school": school, "students_no": students_no, "teachers_no": teachers_no})

# view which shows list of all classes


@view_for("admin")
def class_list(request, sch_pk, type):
    admin = request.user.admin
    school = School.objects.get(admin=admin, pk=sch_pk)
    link_url = reverse(type)

    if type == "admins:manage_teachers":
        # if type is manage_teacher
        user_form = UserCreationForm()
        user_form.fields['first_name'].label += " (Optional)"
        user_form.fields['last_name'].label += " (Optional)"
        user_form.fields['email'].label += " (Optional)"
    else:
        # if type is not manage_teachers
        # assign user form variables to none
        user_form = None

    # Get a list of all classes in school
    all_class = school.class_set.all()
    available_terms = Term.objects.filter(
        school=school).order_by("-current_session", "year")
    return render(request, "admins/class-list.html", {"url": link_url, 'user': request.user, 'type': type, 'userform': user_form, "classes": all_class, "available_terms": available_terms, "school": school})


# View to manage teachers.
@view_for("admin")
def manage_teachers(request, class_pk):
    selected_class = Class.objects.get(pk=class_pk)
    # form for updating teacher info
    form = TeacherForm(instance=selected_class.teacher)
    # if class has no teacher
    if selected_class.teacher == None:
        # Return template with "No teacher in class" message
        return HttpResponse(f'''<div class="alert alert-warning my-3" role="alert">
  No teacher for this class. <a href="#add-teachers" data-toggle="collapse" class="alert-link text-light" onclick="add_class('{selected_class.class_name}');" >Click here to add teacher</a>. 
</div>''')

    return render(request, "admins/manage-teachers-or-parents.html", {"type": "Teacher", "teacher": selected_class.teacher, "form": form})

# view to manage parents


@view_for("admin")
def manage_parents(request, class_pk):
    selected_class = Class.objects.get(pk=class_pk)
    # get all students.
    # To view their parents
    students = selected_class.student_set.all()
    paginator = Paginator(students, 10)
    students = paginator.get_page(request.GET.get("page"))
    return render(request, "admins/manage-teachers-or-parents.html", {"type": "Parent", "students": students, "class_pk": class_pk, })


# Notifications view
@view_for("admin")
def notifications(request, sch_pk):
    admin = request.user.admin
    school = School.objects.get(pk=sch_pk, admin=admin)
    # Get school activity_log or notifications
    activity_log = School_activity_log.objects.filter(Class__school=school)
    # Get total number of notifications
    total_no = activity_log.count()
    # Update the activity_log or notifications as viewed
    School_activity_log.objects.filter(
        Class__school=school, viewed=False).update(viewed=True)
    # Show only 20 notifications at once
    activity_log_paginator = Paginator(activity_log, 20)
    if "page" in request.GET:
        # If more notifications are requested
        try:
            page = request.GET.get("page")
            activity_log = activity_log_paginator.page(page)
            # Notification template
            res = Template('''
			{% load tz %}
			{% for activity in activity_log %}
			<blockquote class="generic-blockquote mt-3" style="background-color:#f2f2f2;">                           <h6 >Date : {{activity.Activity_date_and_time|localtime|date:"N j,Y"}}</h6>
			<hr>
			<h6>Time : {{activity.Activity_date_and_time|localtime|date:"P"}}</h6>
			<hr>
			<b class="text-dark">{{activity.Activity_info}}</b>
			</blockquote>
			{% endfor %}
				  ''').render(Context({"activity_log": activity_log}))
            return HttpResponse(res)

        except EmptyPage:
            return HttpResponseServerError("EMPTY")
    else:
        activity_log = activity_log_paginator.page(1)
    return render(request, "admins/notifications.html", {"activity_log": activity_log, "total_no": total_no, "school" : school })


def coming_soon(request):
    return render(request, "admins/coming_soon.html", {})

# View for creating new term or sessions


@view_for("admin")
def add_sessions(request, sch_pk):
    if request.method == "POST":
        year = request.POST.get("year")
        term = request.POST.get("term")
        school = School.objects.get(admin=request.user.admin, pk=sch_pk)
        print(request.POST)
        try:
            current_term = Term.objects.get_or_create(
                school=school, year=year, term=term)[0]
            print(current_term)
            current_term.set_as_current()
            return HttpResponse(render_alert("Session has been selected successfully"))
        except ValueError:
            return HttpResponseServerError("Invalid session detected")

# View for showing teacher or admin or parents profile


@require_auth
def show_profile(request, type, lookup):
    if type == "school":
        sch = School.objects.get(pk=lookup)
        admin = sch.admin
        return render(request, "admins/show-school-profile.html", {"admin": admin, "school": sch})
    elif type == "teacher":
        teacher = get_user_model().objects.get(username=lookup).teacher
        return render(request, "teachers/show-teachers-profile.html", {"teacher": teacher})
    elif type == "parent":
        parent = get_user_model().objects.get(username=lookup).parent
        return render(request, "parents/show-parent-profile.html", {"parent": parent})
