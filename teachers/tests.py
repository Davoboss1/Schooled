from datetime import date
from django.test import TestCase,Client
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from .models import Admin,School,SchoolUser,Teacher
from admins.tests import Admin_tests
from django.db.models import QuerySet
# Create your tests here.
class test_teacher(TestCase):
    @classmethod
    def setUpTestData(self):
        #Admin test model objects definitions
        admin_user = User.objects.create_user(username="TestUser",password="testpassword",first_name="Test_fn",last_name="Test_ln",email="testemail@gmail.com")
        school_user = SchoolUser.objects.create(user=admin_user,level="Admin")
        admin = Admin.objects.create(school_user=school_user,address="123, Address lagos",date_of_birth="2001-09-15",sex="male",state_of_origin="Lagos state",phone_no="080555555555")
        self.admin = admin
        #School objects definition
        school = School.objects.create(admin=admin,school_name="The test school",school_address="123, Test street. Test area.",type="Secondary_school",approved=True,school_email="testemail@test.com")
        self.school = school
        teacher_user = User.objects.create_user(username="TestUserTeacher",password="testpassword",first_name="Test_fn",last_name="Test_ln",email="testemail@gmail.com")
        teacher_school_user = SchoolUser.objects.create(user=teacher_user,level="Teacher")
        self.teacher = Teacher.objects.create(school_user=teacher_school_user,address="123, Address lagos",date_of_birth="2001-09-15",sex="male",state_of_origin="Lagos state",phone_no="080555555555")
 


    def setUp(self):
        self.client = Client() 
        self.client.login(username="TestUserTeacher",password="testpassword")
         
    def test_teacher_update_profile(self):
        #Get client instanxe and url
        client = self.client
        url = "/teachers/update_profile/"
        #Updated profile data to be posted
        post_data = {'username': 'Nwobo', 'first_name': 'Nneka', 'last_name': 'Nwobo', 'email': 'nwobonneka@yahoo.com', 'address': '123, Allen Street Road.', 'date_of_birth': '1979-10-25', 'sex': 'female', 'state_of_origin': 'Enugu state', 'phone_no': '080431215645'}
        #Post updated data
        res = client.post(url,post_data,HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        #Refresh teacher from db to see updated data
        self.teacher.refresh_from_db()
        #Get all teacher fields value in a dictionary
        teacher_dict = QuerySet(self.teacher).values()[0]
        #Refresh teacher user object from db to see updated data
        self.teacher.school_user.user.refresh_from_db()
        #Get all teacher_user fields value in a dictionary
        #Get all keys in post_data dictionary
        post_data_keys = post_data.keys()

        #Loop through keys to compare post_data and teacher object data
        #Loop from 4th index down. Since the first 4 keys contain user infl
        for k in list(post_data_keys)[4:]:
            # if the instance is date type convert to comparable isoformat
            if isinstance(teacher_dict[k],date):
                teacher_dict[k] = teacher_dict[k].isoformat()
            # Assert that data are equal
            self.assertEqual(post_data[k],teacher_dict[k])
        
        #Compare user information
        user_obj = self.teacher.school_user.user
        self.assertEqual(post_data["username"],user_obj.username)
        self.assertEqual(post_data["first_name"],user_obj.first_name)
        self.assertEqual(post_data["last_name"],user_obj.last_name)
        self.assertEqual(post_data["email"],user_obj.email)
        #Test passsword change
        post_data = {'old_password': 'testpassword', 'new_password1': 'Davo2001', 'new_password2': 'Davo2001'}
        res = client.post(url,post_data,HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.teacher.school_user.user.refresh_from_db()
        self.assertTrue(check_password(post_data["new_password2"],self.teacher.school_user.user.password))


