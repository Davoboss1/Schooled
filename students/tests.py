import random
from datetime import date
from django.test import TestCase,Client
from django.contrib.auth.models import User
from django.shortcuts import reverse
from admins.models import School,SchoolUser,Admin
from teachers.models import Teacher,Class
from parents.models import Parent
from .models import Student,Term,Performance,Attendance
# Create your tests here.

class test_students(TestCase):
    @classmethod
    def setUpTestData(self):
        admin_user = User.objects.create_user(username="TestUser",password="testpassword",first_name="Test_fn",last_name="Test_ln",email="testemail@gmail.com")
        school_user = SchoolUser.objects.create(user=admin_user,level="Admin")
        admin = Admin.objects.create(school_user=school_user,address="123, Address lagos",date_of_birth="2001-09-15",sex="male",state_of_origin="Lagos state",phone_no="080555555555")
        self.admin = admin
        #School objects definition
        school = School.objects.create(admin=admin,school_name="The test school",school_address="123, Test street. Test area.",type="Secondary_school",approved=True,school_email="testemail@test.com")
        self.school = school
        self.current_class = Class.objects.create(class_name="JS2",school=school)
         
        teacher_user = User.objects.create_user(username="TestTeacherUser",password="testpassword",first_name="Test_fn",last_name="Test_ln",email="testemail@gmail.com")
        teacher_school_user = SchoolUser.objects.create(user=teacher_user,level="Teacher")
        self.teacher = Teacher.objects.create(school_user=teacher_school_user,teacher_class=self.current_class,address="123, Address lagos",date_of_birth="2001-09-15",sex="male",state_of_origin="Lagos state",phone_no="080555555555")
        self.teacher_class = Class.objects.create(class_name="SS2",teacher=self.teacher,school=self.school)
        self.term = Term.objects.create(school=self.school,year=2020,term="2nd Term")
        print("Test Data setup")
        

    def setUp(self):
        self.client = Client()
        self.client.login(username="TestTeacherUser",password="testpassword")

    #View to test adding of students and adding students
    def test_add_students(self,name="Helen Bose"):
        #Urls for adding students
        url = reverse("students:update")

        parent_username = name.replace(" ","") + "Parent"
        post_data = {'name': name, 'address': '5 Salami close afromedia,ojo', 'date_of_birth': '2004-07-12', 'sex': 'male', 'state_of_origin': 'Lagos', 'email': 'solomonjohnson@gmail.com', 'phone_no': '08185415249', 'parents': ['', ''], 'username': parent_username, 'password1': 'Parent1234', 'password2': 'Parent1234'}
        res = self.client.post(url,post_data)
        student = Student.objects.get(name=name)
        self.assertTrue(student.parents.exists())
        return student
    
    def test_add_students_with_custom_parents(self,name="Joseph Paul",funame="FirstParent",suname="SecondParent"):
        url = reverse("students:update")
        post_data = {'name': name, 'address': '5 Salami close afromedia,ojo', 'date_of_birth': '2004-07-12', 'sex': 'male', 'state_of_origin': 'Lagos', 'email': 'solomonjohnson@gmail.com', 'phone_no': '08185415249', 'parents': [funame,suname], 'username': '', 'password1': '', 'password2': ''}
        names = (funame,suname)
        for uname in names:
            user = User.objects.create_user(username=uname,password="testpassword",first_name="Parent First Name",last_name="Parent Last Name",email="testemail@gmail.com")
            school_user = SchoolUser.objects.create(user=user,level="Parent")
            Parent.objects.create(school_user=school_user,address="123, Address lagos",date_of_birth="2001-09-15",sex="male",state_of_origin="Lagos state",phone_no="080555555555")


        res = self.client.post(url,post_data)
        student = Student.objects.get(name=name)
        self.assertTrue(student.parents.filter(school_user__user__username=funame).exists())
        self.assertTrue(student.parents.filter(school_user__user__username=suname).exists())
        return student

    def test_update_students(self):
        self.test_add_students("Test Student")
        student = Student.objects.filter(name="Test Student").first()
        url = reverse("students:update_student",args=[student.pk])
        parent1 = create_parent("NewParent1","NewParent1Fname","NewParent1Lname")
        parent2 = create_parent("NewParent2","NewParent2Fname","NewParent2Lname")
        post_data = {'name': 'New Name', 'address': 'New Address', 'date_of_birth': '2002-07-12', 'sex': 'female', 'state_of_origin': 'Lagos state', 'email': 'solomongrandyjohnson@outlook.com', 'phone_no': '08083636386',"fparent":"NewParent1","sparent":"NewParent2"}
        res = self.client.post(url,post_data)
        student.refresh_from_db()
        self.assertEqual(student.name,post_data["name"])
        self.assertEqual(student.address,post_data["address"])    
        self.assertEqual(student.date_of_birth.isoformat(),post_data["date_of_birth"])
        self.assertEqual(student.sex,post_data["sex"])
        self.assertEqual(student.state_of_origin,post_data["state_of_origin"])
        self.assertEqual(student.email,post_data["email"])
        self.assertEqual(student.phone_no,post_data["phone_no"])
        self.assertTrue(student.parents.filter(pk=parent1.pk).exists())

        self.assertTrue(student.parents.filter(pk=parent2.pk).exists())
        return student


    def test_delete_students(self,name="Student Delete"):
        if name == "Student Delete":
            self.test_add_students("Student Delete")

        student_set = Student.objects.filter(name=name)
        url = reverse("students:edit_students")
        self.assertTrue(student_set.exists())
        res = self.client.post(url,{"pk":student_set.first().pk},HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertFalse(Student.objects.filter(name=name).exists())

    def test_performance_creation(self,pk=None):
        if pk is None:
            student1 = self.test_add_students("Frank Patrick")
            student2 = self.test_add_students("Edward Clark")
            student3 = self.test_add_students("Ola Usman")
            student4 = self.test_add_students("Nkechi Chinedu")
            students_list = (student1,student2,student3,student4)
        else:
            students_list = (Student.objects.get(pk=pk))
        for student in students_list:
            subjects = ["Mathematics","English Language","Physics","Chemistry","Geography","Agricultural SScience","Biology","Civic Education"]
            for subject in subjects:
                test = random.randint(0,40)
                exam = random.randint(0,60)
                num = test + exam
                if num < 40:
                    comment = "Poor"
                elif num >= 40 and num <= 49:
                    comment = "Fair"
                elif num >= 50 and num <= 59:
                    comment = "Good"
                elif num >= 60 and num <= 74:
                    comment = "Very Good"
                elif num >= 75:
                    comment = "Excellent"                 
                post_data = {'name': student.name, 'subject': subject, 'test': test, 'exam': exam, 'comment': comment}
                url = "/students/" + str(student.pk) + "/performance/"
                res = self.client.post(url,post_data)
                performance = Performance.objects.filter(student = student,subject=subject,test=test,exam=exam,comment=comment,term=self.term,Class=student.Class)
                self.assertTrue(performance.exists())

    def test_performance_update(self):
        student = self.test_add_students("Patricia Patrick")
        subject = "Music"
        test = 30
        exam = 50
        comment = "Excellent"

        performance = Performance.objects.create(student = student,subject="Music",test=test,exam=exam,comment=comment,term=self.term,Class=student.Class)
        test = 25
        exam = 38
        total = test + exam
        comment = "Very Good"
        post_data = {'name': student.name, 'subject': subject, 'test': test, 'exam': exam, 'comment': comment}
        url = "/students/" + str(student.pk) + "/performance/"
        res = self.client.post(url,post_data)
        performance.refresh_from_db()
        self.assertEqual(performance.subject,subject)
        self.assertEqual(performance.test,test)
        self.assertEqual(performance.exam,exam)
        self.assertEqual(performance.total,total)
        self.assertEqual(performance.comment,comment)

    def test_performance_delete(self):
        student = self.test_add_students("Patricia Frank")
        subjects = ["Mathematics","English Language","Physics","Chemistry","Geography","Agricultural SScience","Biology","Civic Education"]
        for subject in subjects:
            test = random.randint(0,40)
            exam = random.randint(0,60)
            comment = "Participated"
            total = test + exam
            performance = Performance.objects.create(student = student,subject=subject,test=test,exam=exam,comment=comment,term=self.term,Class=student.Class)
            url = reverse("students:delete")
            res = self.client.post(url,{"pk":performance.pk},HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertRaises(Performance.DoesNotExist,performance.refresh_from_db)

    def test_attendance_mark(self,date=date.today()):
        students_list = []
        pk_list = []
        for i in range(5):
            student = self.test_add_students("David Akinfenwa"+str(i))
            students_list.append(student)
            pk_list.append(student.pk)
        post_data = {"present":pk_list[:3]}
        url = reverse("students:mark",args=[date.isoformat()])
        res = self.client.post(url,post_data)
        attendance = Attendance.objects.get(Class=students_list[0].Class,date=date).present_students.all()
        self.assertIn(students_list[0],attendance)
        self.assertIn(students_list[1],attendance)
        self.assertIn(students_list[2],attendance)
        self.assertNotIn(students_list[3],attendance)
        self.assertNotIn(students_list[4],attendance)

    def test_attendance_update(self,date=date.today()):
        Student.objects.all().delete()
        self.test_attendance_mark()
        students = Student.objects.all()
        pk_list = students.values_list("pk",flat=True)
        students_list = list(students)
        post_data = {"present":pk_list[2:]}
        url = reverse("students:mark",args=[date.isoformat()])
        res = self.client.post(url,post_data)
        attendance = Attendance.objects.get(Class=students_list[0].Class,date=date).present_students.all()
        self.assertIn(students_list[4],attendance)
        self.assertIn(students_list[3],attendance)
        self.assertIn(students_list[2],attendance)
        self.assertNotIn(students_list[1],attendance)
        self.assertNotIn(students_list[0],attendance)


def create_parent(username,fname,lname):
    user = User.objects.create_user(username=username,password="testpassword",first_name=fname,last_name=lname,email="testemail@gmail.com")
    school_user = SchoolUser.objects.create(user=user,level="Parent")
    parent = Parent.objects.create(school_user=school_user,address="123, Address lagos",date_of_birth="2001-09-15",sex="male",state_of_origin="Lagos state",phone_no="080555555555")
    return parent

