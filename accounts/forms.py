from django.contrib.auth.forms import UserCreationForm,SetPasswordForm
from django.forms import ModelForm
from django.contrib.auth import get_user_model
class UserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username','password1','password2','first_name','last_name','email')


class UserUpdateForm(ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('username','first_name','last_name','email')

