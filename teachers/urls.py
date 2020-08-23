from  django.urls import  path,re_path
from django.shortcuts import redirect,reverse
from . import views

urlpatterns = [
		path('', views.teacher_homepage, name='teacher_homepage'),
		re_path("^show-.*",lambda x:redirect(reverse("teacher_homepage"))),
		path('create/', views.teacher_create, name='teacher_create'),
	path("update_profile/",views.update_profile,name="update_profile"),	path("teacher_update/<pk>/",views.teacher_update,name="teacher_update"),
		path("teacher_delete/",views.teacher_delete,name="teacher_delete"),
		path("update_class",views.update_class,name="update_class")

]
