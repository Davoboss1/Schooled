from datetime import date
from django.test import TestCase,Client
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from .models import Parent,SchoolUser
from admins.tests import Admin_tests
from django.db.models import QuerySet
# Create your tests here.
class test_parents(TestCase):
    @classmethod
    def setUpTestData(self):
        #Admin test model objects definitions
        self.parent = create_parent("TestParent","TPFN","TPSN")

    def setUp(self):
        #self.parent.school_user.user.set_password("testpassword")
        self.client = Client() 
        self.client.login(username="TestParent",password="testpassword")
    
        print("Test update user info")
    def test_parents_update_user_info(self):
        url = "/parents/update/"
        post_data = {'type': 'Username', 'username': 'DavidAkinfenwaParent', 'first_name': 'David', 'last_name': 'Akinfenwa', 'email': 'davidakinfenwa2@gmail.com'}
        self.client.post(url,post_data,HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        user_obj = self.parent.school_user.user
        user_obj.refresh_from_db()
        self.assertEqual(post_data["username"],user_obj.username)
        self.assertEqual(post_data["first_name"],user_obj.first_name)
        self.assertEqual(post_data["last_name"],user_obj.last_name)
        self.assertEqual(post_data["email"],user_obj.email)


    def test_parents_update_password(self):
        url = "/parents/update/"
        post_data = {'type': 'Password', 'old_password': 'testpassword', 'new_password1': 'Davo2001', 'new_password2': 'Davo2001'}
        self.client.post(url,post_data,HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.parent.school_user.user.refresh_from_db()
        self.assertTrue(check_password(post_data["new_password2"],self.parent.school_user.user.password))
         
         
    def test_parents_update_details(self):     
        url = "/parents/update/"
        post_data = {'type': 'Info', 'address': '22, Adegbemileke street , afromedia,ojo', 'date_of_birth': '1986-09-15', 'sex': 'male', 'state_of_origin': 'Oyo state', 'phone_no': '08185415249'}
        self.client.post(url,post_data,HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.parent.refresh_from_db()
        parent_dict = QuerySet(self.parent).values()[0]
        #Get all keys in post_data dictionary
        post_data_keys = post_data.keys()
        #Loop through keys to compare post_data and teacher object data
        for k in list(post_data_keys)[1:]:
            # if the instance is date type convert to comparable isoformat
            if isinstance(parent_dict[k],date):
                parent_dict[k] = parent_dict[k].isoformat()
            # Assert that data are equal
            self.assertEqual(post_data[k],parent_dict[k])


def create_parent(username,fname,lname):
    user = User.objects.create_user(username=username,password="testpassword",first_name=fname,last_name=lname,email="testemail@gmail.com")
    school_user = SchoolUser.objects.create(user=user,level="Parent")
    parent = Parent.objects.create(school_user=school_user,address="123, Address lagos",date_of_birth="2001-09-15",sex="male",state_of_origin="Lagos state",phone_no="080555555555")
    return parent

