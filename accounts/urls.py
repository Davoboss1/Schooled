from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

app_name = "accounts"
urlpatterns = [
	path('register/', views.register, name='register'),
	path('welcome_page/',views.welcome_page,name="welcome_page"),
	path('login/', views.account_login.as_view(), name= 'login'),
	path("reset_password",views.reset_password,name="reset_password"),
	path('logout/', LogoutView.as_view(template_name='accounts/admin_logout.html'), name= 'logout'),
	path('account_redirect/',views.account_handler, name = 'accounts_handler'),
]

