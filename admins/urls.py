from django.urls import path,re_path
from django.shortcuts import redirect,reverse
from . import views

urlpatterns = [
#School_owner
path("",views.school_owner_home_page, name='admin_homepage'),
re_path("^view-.*",lambda x:redirect(reverse("admin_homepage"))),
path("create_new_school/",views.create_new_school,name="create_new_school"),
path("delete_school/",views.delete_school,name="delete_school"),
path("profile/",views.school_profile,name="school_profile"),
path("profile/<int:sch_pk>/",views.school_profile,name="school_profile"),

path("class/<str:type>/",views.class_list,name="class_list"),
path("class/<str:type>/<int:sch_pk>/",views.class_list,name="class_list"),
path("view_performance/",views.view_performance,name="view_performance"),
path("view_performance/<pk>/",views.view_performance,name="view_performance"),

path("view_attendance/",views.view_attendance,name="view_attendance"),
path("view_attendance/<pk>/",views.view_attendance,name="view_attendance"),

path("student_info/",views.view_student_info,name="view_student_info"),
path("student_info/<pk>/",views.view_student_info,name="view_student_info"),
path("manage_teachers/",views.manage_teachers,name="manage_teachers"),

path("manage_teachers/<class_pk>/",views.manage_teachers,name="manage_teachers"),

path("manage_parents/",views.manage_parents,name="manage_parents"),
path("manage_parents/<class_pk>/",views.manage_parents,name="manage_parents"),
path("notifications/",views.notifications,name="notifications"),
path("notifications/<int:sch_pk>/",views.notifications,name="notifications"),
path("profile_page/",views.profile_page,name="profile_page"),
path("profile_page/<pk>/",views.profile_page,name="profile_page"),
path("add_sessions/",views.add_sessions,name="add_sessions"),
path("add_sessions/<int:sch_pk>/",views.add_sessions,name="add_sessions"),
path("show_profile/",views.show_profile,name="show_profile"),
path("show_profile/<str:type>/<lookup>/",views.show_profile,name="show_profile"),
path("coming_soon/",views.coming_soon,name="coming_soon"),
path("coming_soon/<int:pk>/",views.coming_soon,name="coming_soon")

]
