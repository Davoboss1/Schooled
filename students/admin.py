from django.contrib import admin
from .models import Student, Performance, Attendance,Term,School_activity_log

# Register your models here.
admin.site.register(Student)
admin.site.register(Performance)
admin.site.register(Attendance)
admin.site.register(Term)
admin.site.register(School_activity_log)

