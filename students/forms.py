from django.forms import ModelForm,TextInput,widgets

from .models import Student, Performance, Attendance
		
class StudentForm(ModelForm):

    class Meta:
        model = Student
        fields = ['name', 'address','date_of_birth', 'sex','state_of_origin','email','phone_no']
        labels = {'email':'Email (Optional)','phone_no':'Phone number (Optional)'} 
        widgets = {"name":widgets.TextInput(attrs={"autofocus":"autofocus"}),"date_of_birth":widgets.DateInput(attrs={"class":"form-control","type":"date"}),"phone_no":widgets.TextInput(attrs={"type":"tel"})}
      
class PerformanceForm(ModelForm):
	
	class Meta:
		model = Performance
		fields = ['subject','test','exam','comment']
class AttendanceForm(ModelForm):
	class Meta:
		model = Attendance
		fields = ('__all__')
	
