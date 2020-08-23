
def update_class(request):
	admin = request.user.schooluser.admin
	class_pk = request.POST.get("class_pk")
	class_name = request.POST.get("class_name")
	class_set = Class.objects.get(school__admin=admin,pk=class_pk)
	if class_set.exists():
		class_set.update(class_name=class_name)
		return HttpResponse("Success")
	else:
		return HttpResponseServerError("ERROR")

def send_email(subject,message,recipent):
	if subject and message and recipent:
		try:
			send_mail(subject, message, "links2webcontact@gmail.com", [recipent])
		except BadHeaderError:
			return False
		return True
	else:
		return False


def reset_password(request):
	if "username" in request.GET:
		username = request.GET.get("username")
		user = User.objects.get(username=username)
		v_code = "{:06}".format(random.randint(0,999999))
		token = {"v_code":v_code,"username":username}
		send_email('Schooled password reset verification code','Hello '+username+".\n Your schooled password reset verification code is "+ v_code + ".\n Please note that this code expires after 15 minutes.",user.email)
		set_expirable_session(token,datetime.now() + timedelta(minutes=15))
		return HttpResponse(user.email)

	if request.method == "POST":
		username = request.POST.get("username")
		v_code = request.POST.get("v_code")
		token = get_expirable_session()
		code_valid = (token["username"] == username and token["v_code"] == v_code)
		if code_valid:
			user = User.objects.get(username=username)
			if "password1" in request.POST:
				passwordform = SetPasswordForm(instance=user,request.POST)
				if passwordform.is_valid():
					passwordform.save()
				else:
					return render(request,"accounts/reset_password.html",{"passwordform":passwordform})

			else:
				data = Template('''
					{% load crispy_forms_tags %}
					<input type="text" name="username"  value="{{username}}" readonly>
					<input type="hidden" name="v_code" value="{{v_code}}" >
					{{passwordform|crispy}}
					<button type="submit" class="genric-btn primary radius">Submit</button>
					''').render(Context({"v_code":v_code,"username":username,"passwordform":SetPasswordForm()}))
				return HttpResponse(data)

	return render(request,"accounts/reset_password.html",{})
