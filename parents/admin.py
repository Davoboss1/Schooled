from django.contrib import admin
from .models import  Parent
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Register your models here.
class ParentAdmin(admin.ModelAdmin):
	list_display = ['full_name', 'sex']
	search_fields = ['name']
	

admin.site.register(Parent, ParentAdmin)

