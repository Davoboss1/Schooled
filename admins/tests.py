from django.test import TestCase,Client
from django.contrib.auth.models import User
from django.shortcuts import reverse
from accounts.tests import assert_url_status_code
from admins.models import SchoolUser, School, Admin
from teachers.models import Class,Teacher
from students.models import Term

# Create your tests her.
class Admin_tests(TestCase):
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
         
         
    def setUp(self):
        self.client = Client() 
        self.client.login(username="TestUser",password="testpassword")
     
    def test_admin_pages(self):
        client = self.client
        assert_url_status_code("/admins/",client)
        assert_url_status_code(reverse("school_profile",args=[self.school.pk]),client)
        name_list = ["view_performance","view_attendance","manage_parents","manage_teachers","view_student_info"]
        for name in name_list:
            url = reverse("class_list",args=[name,self.school.pk])
            assert_url_status_code(url,client)
        assert_url_status_code(reverse("message_list",args=[self.school.pk]),client)
        assert_url_status_code(reverse("notifications",args=[self.school.pk]),client)
         
         
    #Test for creation of new session/term
    def test_sessions(self):
        #Request informations
        client = self.client
        url = reverse("add_sessions",args=[self.school.pk])
        #Test data to be posted
        post_data = {"year":2020,"term":"1st Term"}
        res = client.post(url,post_data)
        #Assertions
        #Assert that the right term object is created
        self.assertTrue(Term.objects.filter(school=self.school,year=post_data["year"],term=post_data["term"]).exists())
        res = client.post(url,post_data)
        term_set = Term.objects.filter(school=self.school,year=post_data["year"],term=post_data["term"])
        self.assertTrue(term_set.exists() and term_set.count() == 1)
           
            
             
    #Test for creation of new teacher 
    def test_add_teacher(self,username="Teacher",class_name="JS3"):
        #Request client definition
        client = self.client
        #Data to simulate post request
        post_data = {'username': username, 'password1': 'Davo2001', 'password2': 'Davo2001', 'firstname': 'David', 'lastname': 'Akinfenwa', 'email': 'davidakinfenwa@gmail.com', 'user-profile-picture': '', 'address': '5 Salami close afromedia,ojo', 'date_of_birth': '1983-06-20', 'sex': 'male', 'state_of_origin': 'Oyo state', 'phone_no': '08185415249', 'marital_status': 'Single',"employed_on":"2019-04-15","sch_pk":self.school.pk}
        post_data["class"] = class_name
        #request url
        url = reverse("teacher_create")
        #Test post with all accurate values
        res = client.post(url,post_data)
        #Assertions
        #Test teacher username was creates correctly
        try:
            user = User.objects.get(username=post_data["username"])
        except:
            raise AssertionError("Username does not exists")
        #Test that teacher user model has a schooluser object
        assert (user is not None), "Schooluser was not created"
        #Test that correct schooluser object was created with correct value
        assert (user.level=="Teacher"), "Schooluser is not a teacher"
        #Test that teacher profile was created
        assert (user.teacher is not None), "Schooluser does not have teacher profile"
        #Get query set of class that was created
        #Needed to make some assertions like
        #Check if class exists,class is unique or no duplicates
        class_set = Class.objects.filter(class_name=post_data["class"])
        assert (class_set.exists() and class_set.count()==1), "Class does not exists or is not unique"
        self.assertEqual(user.teacher,class_set.first().teacher)
        return user.teacher

    def test_new_teacher_for_class(self):
        self.test_add_teacher("TeacherTest","JS3") 
        teacher = Teacher.objects.get(school_user__user__username="TeacherTest")
        self.test_delete_teacher(teacher.pk)
        self.test_add_teacher("NewTeacherTest","JS3") 
        current_class = Class.objects.get(class_name="JS3")
        new_teacher = Teacher.objects.get(school_user__user__username="NewTeacherTest")
        self.assertEqual(current_class.teacher.pk,new_teacher.pk)

        

    def test_delete_teacher(self,pk=None):
        client = self.client
        url = reverse("teacher_delete")
        if pk is None:           
            self.test_add_teacher("TestTeacher","SS1")
            teacher = Teacher.objects.get(school_user__user__username="TestTeacher")
            pk = teacher.pk
        else:
            teacher = Teacher.objects.get(pk=pk)
        username = teacher.school_user.user.get_username()
        client.post(url,{"pk":pk})
        self.assertFalse(User.objects.filter(username=username).exists())

         
    def test_view_performance(self):
        client = self.client
        self.test_add_teacher("Teacher2","SS2")
        current_class = Class.objects.get(teacher__school_user__user__username="Teacher2")
        url = reverse("view_performance",args=[current_class.pk])
        res = client.get(url)
         
    def test_view_attendance(self):
        client = self.client
        self.test_add_teacher("Teacher2","SS2")
        current_class = Class.objects.get(teacher__school_user__user__username="Teacher2")
        url = reverse("view_attendance",args=[current_class.pk])
        res = client.get(url)
         
    def test_create_new_school(self,school_name="Test School"):
        client = self.client
        post_data = {'school_name': school_name, 'school_address': '5 Salami close afromedia,ojo', 'type': 'Primary_School', 'approved': 'on', 'motto': 'A school with foundation as solid as gold', 'school_email': 'kiddiesschool@yahoo.com', 'school-image': ''}
        url = reverse("create_new_school")
        client.post(url,post_data)
        self.assertTrue(School.objects.filter(admin=self.admin,school_name=school_name))

    def test_delete_school(self,admin=None,**kwargs):
        if admin is None:
            admin = self.admin
        school_pk = None
        if kwargs.get("name"):
            school_pk = school.objects.get(admin=admin,school_name=kwargs["name"]).pk
        elif kwargs.get("pk"):
            school_pk = school.objects.get(admin=admin,pk=kwargs["pk"]).pk
        else:
            self.test_create_new_school("My school")
            school_pk = School.objects.get(school_name="My school").pk
        client = self.client
        url = reverse("delete_school")
        client.post(url,{"sch_pk":school_pk})
