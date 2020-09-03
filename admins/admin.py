from django.contrib import admin
from .models import School, Admin,Messages,Conversation
# Register your models here.
	
class SchoolAdmin(admin.ModelAdmin):
	list_display = ['school_name', 'type']
	search_fields = ['school_name']
	
class AdminAdmin(admin.ModelAdmin):
	list_display = ['full_name']
	search_fields = ['name']

admin.site.register(School, SchoolAdmin)
admin.site.register(Admin, AdminAdmin)
admin.site.register(Conversation)
admin.site.register(Messages)
