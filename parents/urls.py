from django.urls import path
from . import views

app_name = "parents"
urlpatterns = [	path("parents-homepage/",views.parents_homepage,name="parents_homepage"),
path("update/",views.update,name="update"),
	]