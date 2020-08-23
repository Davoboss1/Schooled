import random
from datetime import date
from teachers.models import Class
from students.models import Student,Performance,Attendance,Term

def performance_create(Class):
    subjects = ["Mathematics","English Language","Basic Science","Basic Tech","C.R.S","P.H.E","Social Studies","Buisness Studies","Yoruba","French","Fine arts","Civic Education","Music","Computer","Vocational Studies"]
    students = Student.objects.all()
    for student in students:
        for subject in subjects:
            test = random.randint(0,40)
            exam = random.randint(0,60)
            total = test + exam
            if total < 40:
               comment = "Poor"
            elif total < 50:
                comment = "Fair"
            elif total < 60:
                comment = "Good"
            elif total < 75:
                comment = "Very Good"
            elif total < 100:
                comment = "Excellent"

            try:
                Performance.objects.create(student=student,subject=subject,Class=Class,term=Term.objects.first(),test=test,exam=exam,comment=comment)
                print(f"{subject} performance is added for {student}")
            except:
                print(f"{subject} performance for {student} failed to add.")


#Tries to generate past 3 months dates excluding weekends
def generate_dates(term,year):
    #Function generates dates for three months excluding weekends
    #Arg term collects 1&3 1 = 1st Term, 2 = 2nd Term, 3 = 3rd Term
    #month var represents last month of the terms
    #1st term ends in november,2nd term match, 3rd term july
    if term == 1:
        month = 11
    elif term == 2:
        month = 3
    elif term == 3:
        month = 7
    #Get day range 1 - 31
    date_range = range(1,32)
    #Month range is the last three months of the term i.e Month July = 7, 
    #Last three months is 7,6,5, July,June,May
    mon_range = [month,month-1,month-2]
    #Intialize list for all dates
    dates_list = []
    for mon in mon_range:
        for day in date_range:
            try:
                d = date(year,mon,day)
            except ValueError:
                continue
            mon_no = int(d.strftime("%u"))
            if mon_no > 5:
                continue
            dates_list.append(d)

    return dates_list


def attendance_create(Class,term,year):
    dates = generate_dates(term,year)
    students = Class.student_set.all().values_list("pk",flat=True)
    for date in dates:
        present_students_no = students.count() -  random.randint(0,15)
        present_students = random.sample(list(students),present_students_no)
        try:
            attendance = Attendance.objects.create(Class=Class,date=date)
            attendance.present_students.set(present_students)
            print("Attendance for " + date.isoformat() + " Added.")
        except:
            print("Attendance for " + date.isoformat() + " Failed to add.")



def delete_all_performance():
    Performance.objects.all().delete()

def delete_all_attendance():
    Attendance.objects.all().delete()
 
def create_students(Class,no):
    names = ["Edward","Patrick","Frank","Bola","Emeka","Joseph","Joshua","James","James","Ayomide","Jessica","Matthew","Usman","Hassan","Chisom","Precious","Emmauel","David","Paul","Philip","Mark","Max","Grace","Helen","Oyin","Luke","Chukwuman","Chidera","Favour","Gift","Raul","Taiwo","Kehinde","Akpors","Olu","Jumoke","Bose","Tope"]
    list_data = []
    count = 0
    for name in names:
        for sname in names:
            if name == sname:
                continue
            fname = name + " " + sname
            list_data.append(fname)
            count+=1
            sfname = sname + " " +  name
            list_data.append(sfname)
            count+=1
    for name in random.sample(list_data,no):
        Student.objects.create(name=name,address='5 Salami close afromedia,ojo',date_of_birth='2004-07-12',sex='male',state_of_origin='Lagos',phone_no='08185415249',email="schoolemail@gmail.com",Class=Class)
        print(f"{name} student for {Class.class_name} added")

def run():
    #print(Class.objects.all())
    #performance_create(Class.objects.get(class_name="JSS 3"))
    create_students(Class.objects.get(class_name="JSS 3"),2000)
    #delete_all_attendance()
    #attendance_create(Class.objects.get(class_name="JSS 3"),3,2020)

