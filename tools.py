from datetime import date as Date ,datetime
from functools import wraps
from django.core.exceptions import PermissionDenied,ValidationError


def require_ajax(func):
    @wraps(func)
    def innerfunc(request,*args,**kwargs):
        if request.is_ajax():
            return func(request,*args,**kwargs)
        else:
            raise PermissionDenied()
    return innerfunc

def require_auth(func):
    @wraps(func)
    def innerfunc(request,*args,**kwargs):
        print(dir(request))
        if request.user.is_authenticated:
            return func(request,*args,**kwargs)
        else:
            raise PermissionDenied()
    return innerfunc

def view_for(type):
    def innerfunc(func):
        @wraps(func)
        def view(request,*args,**kwargs):
            if str(request.user.level).lower() == type.lower():
                return func(request,*args,**kwargs)
            else:
                raise PermissionDenied()
        return view
    return innerfunc

def years_ago(date):
    td = Date.today()
    year = td.year - date.year
    if td.month < date.month :
        year-=1
    elif td.month == date.month:
        if td.day < date.day:
            year-=1
    if year < 0:
        year = 0
    return year

def set_expirable_session(request,key,data,expiry_date):
    request.session[key] = {"data":data,"expiry_date":expiry_date.isoformat()}

def get_expirable_session(request,key):
    session = request.session[key]
    if datetime.fromisoformat(session["expiry_date"]) < datetime.now():
        del request.session[key]
        raise ValidationError("Session has expired")
    else:
        return session["data"]

#Saves image to image field while deleting previous image
def save_picture(image_field,picture_file):
	if picture_file is not None:
		#Check if file.is not default image
		if image_field.name != "default.jpg":
			try:
				image_field.delete()
			except ValueError:
				pass
		image_field.save(picture_file.name,picture_file.file,save=True)
		return True
	else:
		return False

