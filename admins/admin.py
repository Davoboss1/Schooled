from django.contrib import admin
from .models import School, Admin
# Register your models here.
	
class SchoolAdmin(admin.ModelAdmin):
	list_display = ['school_name', 'type']
	search_fields = ['school_name']
	
class AdminAdmin(admin.ModelAdmin):
	list_display = ['full_name']
	search_fields = ['name']

admin.site.register(School, SchoolAdmin)
admin.site.register(Admin, AdminAdmin)
