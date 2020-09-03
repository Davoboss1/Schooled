from django.contrib import admin
from .models import Teacher,Class

# Register your models here.
class TeacherAdmin(admin.ModelAdmin):
	list_display = ['full_name']
	search_fields = ['user']
	ordering = ['user']
	
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Class)
