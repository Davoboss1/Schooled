from .models import Parent
from django.forms import ModelForm,widgets


class ParentForm(ModelForm):
	class Meta:
		model = Parent
		fields = ('__all__')
		exclude = ("school","user")
		widgets = {"date_of_birth" : widgets.DateInput(attrs={"type":"date",},),"phone_no" : widgets.TextInput(attrs={"type":"tel",},),}
			
