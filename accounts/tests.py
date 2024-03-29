from django.test import TestCase,Client
from django.template import Context
from admins.models import School,Admin
from teachers.models import Teacher,Class
from parents.models import Parent
from django.contrib.auth.models import AnonymousUser
from .models import User
# Create your tests here.
class accounts_test(TestCase):
    @classmethod
    def setUpTestData(self):
        #Admin test model objects definitions
        admin_user = User.objects.create_user(username="TestUser",password="testpassword",first_name="Test_fn",last_name="Test_ln",email="testemail@gmail.com")
        admin = Admin.objects.create(user=admin_user,address="123, Address lagos",phone_no="080555555555")
        #School objects definition
        school = School.objects.create(admin=admin,school_name="The test school",school_address="123, Test street. Test area.",type="Secondary_school",approved=True,school_email="testemail@test.com")
        teacher_user = User.objects.create_user(username="TeacherTestUser",password="testpassword",first_name="Test_fn",last_name="Test_ln",email="testemail@gmail.com")
        teacher = Teacher.objects.create(user=teacher_user,address="123, Address lagos",phone_no="080555555555")
        teacher_class = Class.objects.create(teacher=teacher,school=school,class_name="JS1")

        #Parents model objects definition
        parent_user = User.objects.create_user(username="ParentTestUser",password="testpassword",first_name="Test_fn",last_name="Test_ln",email="testemail@gmail.com")
        parent = Parent.objects.create(user=parent_user,address="123, Address lagos",phone_no="080555555555")
        
    def test_redirects(self):
        client = Client()
        response = client.get("/")
        self.assertRedirects(response,'/accounts/welcome_page/',target_status_code=200)
        client.login(username="TestUser",password="testpassword")
        response = client.get("/")
        self.assertRedirects(response,'/admins/')
        client.logout()
        client.login(username="TeacherTestUser",password="testpassword")
        response = client.get("/")
        self.assertRedirects(response,'/teachers/')
        client.logout()
        client.login(username="ParentTestUser",password="testpassword")
        response = client.get("/")
        self.assertRedirects(response,'/parents/parents-homepage/')
        response = client.get("/accounts/logout/")
        self.assertEqual(response.wsgi_request.user,AnonymousUser())
    
    def test_urls_response(self):
        assert_url_status_code("/accounts/welcome_page/")
        assert_url_status_code("/accounts/login/")
        assert_url_status_code("/accounts/register/")
        assert_url_status_code("/accounts/logout/")
        print("Urls status tested")
        
    def test_register(self):
        client = Client()
        post_data = {'username': 'Admin', 'password1': 'Davo2001', 'password2': 'Davo2001', 'firstname': 'David', 'lastname': 'Akinfenwa', 'email': 'davidakinfenwa@gmail.com', 'address': '5 Salami close afromedia,ojo', 'phone_no': '08185415249', 'school_name': 'Test Comprehensive School', 'school_address': '5 Salami close afromedia,ojo', 'type': 'Secondary_School', 'approved': True, 'motto': '', 'school_email': 'testschool@email.com'}
        response = client.post("/accounts/register/",post_data)
        username = post_data['username']
        school_name = post_data['school_name']
        user = User.objects.get(username=username)
        self.assertEqual(user.first_name,post_data["firstname"])
        self.assertEqual(user.last_name,post_data["lastname"])
        self.assertEqual(user.email,post_data["email"])
        self.assertTrue(User.objects.filter(username=username).exists())
        assert user is not None, "user schooluser does not exists"
        assert user.admin is not None, "user Admin does not exists"
        self.assertEqual(user.level,"Admin")
        self.assertTrue(School.objects.filter(school_name=school_name).exists())
        
        
def assert_url_status_code(url,client=Client()):
    res = client.get(url)
    t= TestCase()
    t.assertEqual(res.status_code,200)
