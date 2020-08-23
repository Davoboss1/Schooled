from django.test import TestCase
from .models import Term
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from admins.models import School,Admin,SchoolUser
# Create your tests here.

class students_models(TestCase):
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
    
    '''
    def test_unique_term(self):
        school = self.school
        Term.objects.all().delete()
        Term.objects.create(school=school,year=2020,term="1st Term")
        with self.assertRaisesMessage(IntegrityError,"UNIQUE constraint failed: students_term.term, students_term.year") or self.assertRaisesMessage(ValidationError,"Invalid value for next term"):
            Term.objects.create(school=school,year=2020,term="1st Term")
    '''
    def test_previous_term(self):
        with self.assertRaisesMessage(IntegrityError,"CHECK constraint failed: previous_year"):
            Term.objects.create(school=self.school,year=2019,term="3rd Term")

    def test_term_errors(self):
        Term.objects.all().delete()
        Term.objects.create(school=self.school,year=2020,term="1st Term")
        with self.assertRaisesMessage(ValidationError,"Invalid value for next term"):
            Term.objects.create(school=self.school,year=2020,term="3rd Term")
        
        Term.objects.create(school=self.school,year=2020,term="2nd Term")
        with self.assertRaisesMessage(ValidationError,"Invalid value for next term"):
            Term.objects.create(school=self.school,year=2020,term="1st Term")
        Term.objects.create(school=self.school,year=2020,term="3rd Term")
        with self.assertRaisesMessage(ValidationError,"Invalid value for next term"):
            Term.objects.create(school=self.school,year=2021,term="2nd Term")
        Term.objects.create(school=self.school,year=2021,term="1st Term")
        with self.assertRaisesMessage(ValidationError,"Invalid value for next term"):
            Term.objects.create(school=self.school,year=2022,term="2nd Term")
        print(Term.objects.all())
 
