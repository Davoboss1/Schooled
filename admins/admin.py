from django.contrib import admin
from .models import School, Admin,SchoolUser,Messages,Conversation
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
# Register your models here.
class SchoolUserInline(admin.StackedInline):
	model = SchoolUser
	can_delete = False
	verbose_name = "School User"
	
class UserAdmin(BaseUserAdmin):
	inlines = (SchoolUserInline,)
	
	
class SchoolAdmin(admin.ModelAdmin):
	list_display = ['school_name', 'type']
	search_fields = ['school_name']
	
class AdminAdmin(admin.ModelAdmin):
	list_display = ['full_name', 'age']
	search_fields = ['name']

admin.site.unregister(User)
admin.site.register(User,UserAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(Admin, AdminAdmin)
admin.site.register(Conversation)
admin.site.register(Messages)
