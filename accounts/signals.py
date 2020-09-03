import os
from django.db.models.signals import pre_save,post_save,post_delete
from django.contrib.auth import get_user_model
from admins.models import Conversation,Messages


def user_pre_save(sender,instance,**kwargs):
    if instance.pk is not None:
        #Pass previous_username to instance so post_save can use the value
        instance.previous_username = sender.objects.get(id=instance.id).username

def user_post_save(sender,instance,created,**kwargs):
    if not created:
        #Get previous_username and current username
        previous_username = instance.previous_username
        username = instance.username
        #Update every previous_username conversation and messages data with new username
        Conversation.objects.filter(sender=previous_username).update(sender=username)
        Messages.objects.filter(sent_by=previous_username).update(sent_by=username)

def user_post_delete(sender,instance,**kwargs):
	#if user deleted, delete profile_picture
	profile_picture  = instance.profile_picture
	if profile_picture.name != "default.jpg":
		os.remove(profile_picture.path)

pre_save.connect(user_pre_save,sender=get_user_model())
post_save.connect(user_post_save,sender=get_user_model())
post_delete.connect(user_post_delete,sender=get_user_model())
