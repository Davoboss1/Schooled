from django.contrib import admin
from .models import  Parent
from django.contrib.auth import get_user_model

# Register your models here.
class ParentAdmin(admin.ModelAdmin):
	list_display = ['full_name']
	search_fields = ['name']
	

admin.site.register(Parent, ParentAdmin)

