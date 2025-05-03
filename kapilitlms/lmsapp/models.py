from django.db import models
import uuid
import random
from datetime import timedelta
from django.utils.timezone import now
from django.db import models
# from django.contrib.postgres.fields import ArrayField
from django.db.models import JSONField

#Manager model

class Manager(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    employee_id = models.CharField(max_length=10, unique=True)
    role = models.CharField(max_length=50, default='Manager')
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.employee_id})"

#Trainer model

class Trainer(models.Model):
     COURSE_CHOICES = [
        ('Python Programming', 'Python Programming'),
        ('Java Programming', 'Java Programming'),
        ('Data Science', 'Data Science'),
        ('Data Analytics', 'Data Analytics'),
        ('DevOps cum AWS', 'DevOps cum AWS'),
        ('Cyber Security', 'Cyber Security'),
        ('Communication', 'Communication'),
        ('Aptitude', 'Aptitude'),
    ]
     
     manager = models.ForeignKey(Manager, on_delete=models.CASCADE, related_name='trainers')
     name = models.CharField(max_length=100)
     email = models.EmailField(unique=True)
     employee_id = models.CharField(max_length=10, unique=True)
     role = models.CharField(max_length=50, default='Trainer')
     course = models.CharField(max_length=50, choices=COURSE_CHOICES)
     subjects = JSONField(default=list)
     status = models.BooleanField(default=True)
     added_on = models.DateTimeField(default=now)

     def __str__(self):
         return f"{self.name} ({self.role}) - {self.course} (Managed by: {self.manager.name})"
     

class AssessmentDetails(models.Model):
    ASSESSMENT_STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    manager = models.ForeignKey('Manager', on_delete=models.CASCADE, related_name='assessments')
    trainer = models.ForeignKey('Trainer', on_delete=models.CASCADE, related_name='assessments')
    assessment_type = models.CharField(max_length=100)
    number_of_questions = models.IntegerField()
    number_of_mcq = models.IntegerField(default=0)
    number_of_programs = models.IntegerField(default=0)
    assessment_name = models.CharField(max_length=200, unique=True)
    assessment_status = models.CharField(max_length=10, choices=ASSESSMENT_STATUS_CHOICES, default='Active')
    created_by = models.CharField(max_length=100)  # Creator's name (Manager/Trainer/Admin)
    added_on = models.DateTimeField(default=now)  # Timestamp for when the assessment was added
    paper_added_status = models.IntegerField(default=0)
    status = models.BooleanField(default=True)  # Default status is True (active)


    def __str__(self):
        return f"{self.assessment_name} {self.assessment_status}"


class AssessmentPaper(models.Model):
    manager = models.ForeignKey('Manager', on_delete=models.CASCADE, related_name='assessments_paper')
    trainer = models.ForeignKey('Trainer', on_delete=models.CASCADE, related_name='assessments_paper')
    assessment = models.ForeignKey('AssessmentDetails', on_delete=models.CASCADE, related_name='assessments_paper')
    assessment_date = models.DateField()
    assessment_duration = models.CharField(max_length=10)
    questions = models.JSONField()
    question_files = models.JSONField()
    course_name = models.CharField(max_length=150)
    assessment_name = models.CharField(max_length=200)
    created_by = models.CharField(max_length=100)
    added_on = models.DateTimeField(default=now)
    status = models.BooleanField(default=True)



#kapil student signin page model

class Kapil_Student(models.Model):
    COURSE_CHOICE =[
        ('PYTHON','Python Programming'),
        ('JAVA','Java programming'),
        ('DATA_SCIENCE','Data Science'),
        ('DATA_ANALYTICS','Data Analytics'),
        ('DEVOPS','Devops cum AWS'),
        ('CYBEER_SECURITY','Cyber security'),
        ('COMMUNICATION','Communication'),
        ('APTITUDE','Aptitude')
    ]
    manager = models.ForeignKey('Manager', on_delete=models.CASCADE, related_name='students')
    trainer = models.JSONField(default=list)
    student_name = models.CharField(max_length=100)
    enrollment_id = models.CharField(max_length=100,unique=True)
    mobile= models.CharField(max_length=10,unique=True,null=True)
    email = models.EmailField(max_length=100)
    otp = models.CharField(max_length=6,blank=True,null=True)
    course = models.CharField(max_length=100,choices=COURSE_CHOICE)
    password =  models.CharField(max_length=100)
    confirm_password = models.CharField(max_length=100)
    verification_reset_link = models.UUIDField(default=uuid.uuid4, unique=True,null=True,blank=True)
    register_status = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    password_changed_on = models.DateField(null=True, blank=True)
    trainer_selected = models.BooleanField(default=False)

    # verification_token = models.CharField(max_length=100, null=True, blank=True)

    # def genrate_otp(self):
    #     self.Otp = str (random.randint(100000-999999))
    #     self.Otp_expiry = now() + timedelta(minutes=5)
    #     self.save()

    def _str_(self):
        return self.Student_name
    


#non-kapil-student

class Non_kapil_student(models.Model):
    BRANCH_CHOICES=[
        ('CSE','Computer Science and Engineering'),
        ('CE','Civil Engineering'),
        ('IT','Information Techonologhy'),
        ('ME','mechanical enf=gineering'),
        ('EE','Electical Engineering'),
        ('AE','Automobile Engineering'),
        ('DESIGN','Design and Architecture'),
        ('RE','Robotics Engineering')
    ]
    YEAR_CHOICES =[
        ('1','1st year'),
        ('2','2nd year'),
        ('3','3rd year'),
        ('4','4th year')
    ]
    COURSE_CHOICES = [
        ('PYTHON', 'Python Programming'),
        ('JAVA', 'Java Programming'),
        ('DATA_SCIENCE', 'Data Science'),
        ('DATA_ANALYTICS', 'Data Analytics'),
        ('DEVOPS', 'Devops cum AWS'),
        ('CYBER_SECURITY', 'Cyber Security'),
        ('COMMUNICATION', 'Communication'),
        ('Aptitude', 'Aptitude'),
    ]
    Student_name = models.CharField(max_length=50)
    Qualification = models.CharField(max_length=100)
    Branch = models.CharField(max_length=100,choices=BRANCH_CHOICES)
    College_name =  models.CharField(max_length=100)
    Current_year = models.CharField(max_length=100,choices=YEAR_CHOICES)
    Mobile = models.CharField(max_length=100)
    Email = models.EmailField(max_length=100)
    Password = models.CharField(max_length=100)
    Confirm_password = models.CharField(max_length=100)
    Course = models.CharField(max_length=100,choices=COURSE_CHOICES)
    Otp =models.CharField(max_length=6,blank=True,null=True)
    Verification_reset_link = models.UUIDField(default=uuid.uuid4, unique=True,null=True,blank=True)
    register_status = models.IntegerField(default=0)
    created_on = models.DateField(auto_now_add=True)
    password_changed_on = models.DateField(null=True, blank=True)
    # verification_token = models.CharField(max_length=100, null=True, blank=True)


    # def genrate_otp(self):
    #     # self.Otp = str (random.randint(100000-999999))
    #     self.Otp_expiry = now() + timedelta(minutes=5)
    #     self.save()

    def __str__(self):
        return self.Student_name