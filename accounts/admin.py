#Core Django Dependencies
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User,help,Conversation,Messages
	
admin.site.register(User, UserAdmin)
admin.site.register(help)
admin.site.register(Conversation)
admin.site.register(Messages)
