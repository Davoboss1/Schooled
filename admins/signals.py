import os
from django.db.models.signals import post_delete
from admins.models import School
def school_post_delete(sender,instance,**kwargs):
	image = instance.image
	if image.name != "default.jpg":
		os.remove(image.path)

post_delete.connect(school_post_delete,sender=School)
