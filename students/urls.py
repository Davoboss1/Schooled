from django.urls import path

from . import views

app_name = "students"
#Function Base Views
urlpatterns = [
	#Perfomance URLS
	path('performance/<type>/', views.performance_page, name='performance_page',),	
		path('<student_id>/performance/', views.p_create_or_update, name='performance_update'),
	path('delete/', views.delete, name='delete'),
	
	#Attendance URLS
	path('attendance/<type>/', views.attendance_page, name='attendance_page'),
	path('students/attendance/mark/<Date>/', views.mark, name='mark'),
	
	#Other URLS	
	path("edit_students/",views.edit_students,name='edit_students')
	,
	path('update/', views.update, name='update'),
path('update_student/',views.update_students,name="update_student"),
path('update_student/<pk>/',views.update_students,name="update_student"),
path("convert_attendance_to_pdf/",views.convert_attendance_to_pdf,name="convert_attendance_to_pdf"),
path("convert_attendance_to_pdf/<pk>/",views.convert_attendance_to_pdf,name="convert_attendance_to_pdf"),
path("convert_attendance_to_pdf/<pk>/<start_date>/<end_date>/",views.convert_attendance_to_pdf,name="convert_attendance_to_pdf"),
path("convert_performance_to_pdf/",views.convert_performance_to_pdf,name="convert_performance_to_pdf"),
path("convert_performance_to_pdf/<pk>/<year>/<term>/",views.convert_performance_to_pdf,name="convert_performance_to_pdf"),
path("print_attendance/",views.print_attendance,name="print_attendance"),
path("print_attendance/<pk>/",views.print_attendance,name="print_attendance"),
path("print_attendance/<pk>/<start_date>/<end_date>/",views.print_attendance,name="print_attendance"),
path("print_performance/",views.print_performance,name="print_performance"),
path("print_performance/<pk>/<year>/<term>/",views.print_performance,name="print_performance"),
path('handle_uploads/',views.handle_uploads,name="handle_uploads"),
path("view-only-attendance/",views.view_only_attendance,name="view_only_attendance"),
path("view-only-attendance/<pk>/",views.view_only_attendance,name="view_only_attendance"),
path("view-only-performance/",views.view_only_performance,name="view_only_performance"),
path("view-only-performance/<pk>/",views.view_only_performance,name="view_only_performance"),
path("csv_handler",views.csv_handler,name="csv_handler")
]
