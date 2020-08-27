from django import template
from django.contrib.auth.models import User
from students.models import Term
from admins.models import School
register = template.Library()

#filters performance by term in templates
@register.filter(name="current_term_filter")
def current_term_filter(value):
	try:
		term = Term.objects.get(school=value.Class.school,current_session=True)
		performance = term.performance_set.filter(student=value)
		return performance
	except:
		return None

#returns user object from the username
@register.filter(name="get_user")
def get_user(value):
	try:
		user = User.objects.get(username=value)
		return user
	except:
		return "Unavailable user"

#returns a parent children in a particular school
@register.filter(name="get_children")
def get_children_in_school_from_parents(parent,sch_pk):
    school =  School.objects.get(pk=sch_pk)
    children = parent.student_set.filter(Class__school=school)
    return children


