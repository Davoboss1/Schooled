from django.forms import ModelForm, widgets

from .models import Teacher

class TeacherForm(ModelForm):
	class Meta:
		model = Teacher
		fields = ('__all__')
		exclude = ('school','user')
		widgets = {"date_of_birth":widgets.DateInput(attrs={"type":"date",}),"phone_no":widgets.TextInput(attrs={"type":"tel"},), "image":widgets.FileInput(attrs={"class":"form-control",},),"employed_on":widgets.DateInput(attrs={"type":"date",}),}
		
		
		
		
		
