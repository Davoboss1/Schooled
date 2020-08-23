from datetime import date
from django import template

register = template.Library()

@register.filter(name="to_list")
def to_list(value):
	return list(value)

@register.filter(name="to_date")
def to_date(value):
    Date = date.fromisoformat(value)
    return Date
