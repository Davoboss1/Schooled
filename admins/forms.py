from django.forms import ModelForm, TextInput,widgets

from .models import Admin, School

class AdminForm(ModelForm):
	class Meta:
		model = Admin
		fields = ('__all__')
		exclude = ('school','school_user','created_at','update_at')
		tel = widgets.TextInput(attrs={"type":"tel"})
		widgets = {"date_of_birth":widgets.DateInput(attrs={"type":"date"},),"phone_no":tel}
		
		
class SchoolForm(ModelForm):
	class Meta:
		model = School
		fields = ('__all__')
		exclude= ('admin','image','created_at','update_at')
		textarea = widgets.Textarea(attrs={"rows":5})
		date = widgets.DateInput(attrs={"type":"date"},)
		widgets = {"created_at":date,"update_at":date,"motto":textarea,"school_Anthem":textarea,"vision":textarea,"mission":textarea,}
		
		
		
		
		