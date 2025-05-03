from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect,get_object_or_404, redirect
from django.contrib import messages
import json
import re
import os
from django.db.models import Max
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from lmsapp.models import Kapil_Student, Non_kapil_student, Manager,Trainer,AssessmentDetails,AssessmentPaper
import uuid
import random
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.utils.timezone import now, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.dateformat import DateFormat
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist
import threading
import datetime


def format_duration(duration):
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600  # Get the number of hours
    minutes = (total_seconds % 3600) // 60  # Get the number of minutes
    return f"{hours:02}:{minutes:02}"  # Format as HH:MM

def manager_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        employee_id = request.POST.get('employee_id').lower()

        try:
            manager = Manager.objects.get(email=email, employee_id=employee_id)

            if manager.role == 'manager' and manager.status == 1:
                # Store the manager's id in the session
                request.session['manager_id'] = manager.id
                return redirect('manager_dashboard')
            else:
                messages.error(request, 'Invalid credentials or inactive manager.')
                return redirect('manager_login')
        except Manager.DoesNotExist:
            messages.error(request, 'Manager not found or invalid credentials.')
            return redirect('manager_login')

    return render(request, 'manager/manager_login.html')


def manager_dashboard(request):
    manager_id = request.session.get('manager_id')

    if manager_id:
        try:
            manager = Manager.objects.get(id=manager_id)
            if manager.role == 'manager' and manager.status == 1:
                trainer_count = Trainer.objects.filter(manager=manager).count()
                return render(request, 'manager/manager_dashboard.html', {'manager': manager,'trainer_count': trainer_count})
            else:
                messages.error(request, 'Inactive or invalid manager.')
                return redirect('manager_login')

        except Manager.DoesNotExist:
            messages.error(request, 'Manager not found.')
            return redirect('manager_login')
    else:
        messages.error(request, 'Please log in first.')
        return redirect('manager_login')


def add_trainer(request):
    manager_id = request.session.get('manager_id')

    if manager_id:
        try:
            # Fetch manager using session data
            manager = Manager.objects.get(id=manager_id)

            if manager.role == 'manager':
                if request.method == 'POST':
                    name = request.POST.get('name')
                    email = request.POST.get('email')
                    employee_id = request.POST.get('employee_id').lower()
                    course = request.POST.get('course')
                    status = request.POST.get('status') == 'on'
                    subjects = request.POST.getlist('subjects')  # Gets list of selected subjects

                    try:
                        if Trainer.objects.filter(email=email).exists():
                            messages.error(request, "Trainer email already exists.")
                            return redirect('add_trainer')

                        if Trainer.objects.filter(employee_id=employee_id).exists():
                            messages.error(request, "Trainer Employee ID already exists.")
                            return redirect('add_trainer')

                        # Create a trainer with the manager associated
                        trainer = Trainer(
                            name=name,
                            email=email,
                            employee_id=employee_id,
                            course=course,
                            status=status,
                            manager=manager,  # Use the manager from the session
                            subjects=subjects,

                        )
                        trainer.save()
                        messages.success(request, 'Trainer added successfully!')
                        return redirect('view_trainers')

                    except Exception as e:
                        messages.error(request, f"Error: {e}")
                        return redirect('add_trainer')

                return render(request, 'manager/add_trainer.html', {'manager': manager})
            else:
                messages.error(request, 'You must be logged in as a manager to add a trainer.')
                return redirect('manager_login')

        except Manager.DoesNotExist:
            messages.error(request, 'Manager not found. Please log in again.')
            return redirect('manager_login')

    else:
        messages.error(request, 'Please log in first.')
        return redirect('manager_login')

def view_trainers(request):
    manager_id = request.session.get('manager_id')
    if manager_id:
        try:
            manager = Manager.objects.get(id=manager_id)
            if manager.role == 'manager':
                trainers = Trainer.objects.filter(manager=manager)
                return render(request, 'manager/view_trainers.html', {'trainers': trainers, 'manager': manager})
            else:
                messages.error(request, 'You must be logged in as a manager to view trainers.')
                return redirect('manager_login')        
        except Manager.DoesNotExist:
            messages.error(request, 'Manager not found. Please log in again.')
            return redirect('manager_login')    
    else:
        messages.error(request, 'Please log in first.')
        return redirect('manager_login')

def edit_trainer(request, trainer_id):
    manager_id = request.session.get('manager_id')

    if manager_id:
        try:
            manager = Manager.objects.get(id=manager_id)
            if manager.role == 'manager':
                try:
                    trainer = get_object_or_404(Trainer, id=trainer_id)

                    if request.method == 'POST':
                        # Get new form values
                        name = request.POST.get('name')
                        email = request.POST.get('email')
                        employee_id = request.POST.get('employee_id')
                        course = request.POST.get('course')

                        # Check if the new email or employee ID already exists
                        if Trainer.objects.filter(email=email).exclude(id=trainer.id).exists():
                            messages.error(request, "Email already exists with another trainer!.")
                            return redirect('edit_trainer', trainer_id=trainer.id)

                        if Trainer.objects.filter(employee_id=employee_id).exclude(id=trainer.id).exists():
                            messages.error(request, "Employee Id already exists with another trainer!.")
                            return redirect('edit_trainer', trainer_id=trainer.id)

                        # If no duplicates, update the trainer's details
                        trainer.name = name
                        trainer.email = email
                        trainer.employee_id = employee_id
                        trainer.course = course

                        try:
                            trainer.save()
                            messages.success(request, 'Trainer details updated successfully!')
                            return redirect('view_trainers')  # Redirect after saving

                        except Exception as e:
                            messages.error(request, f"Error: {e}")
                            return redirect('edit_trainer', trainer_id=trainer.id)

                    # Render the edit form with the existing trainer data
                    return render(request, 'manager/edit_trainer.html', {'trainer': trainer})

                except Trainer.DoesNotExist:
                    messages.error(request, 'Trainer not found.')
                    return redirect('view_trainers')

            else:
                messages.error(request, 'You must be logged in as a manager to edit a trainer.')
                return redirect('manager_login')

        except Manager.DoesNotExist:
            messages.error(request, 'Manager not found. Please log in again.')
            return redirect('manager_login')

    else:
        messages.error(request, 'Please log in first.')
        return redirect('manager_login')
def delete_trainer(request, trainer_id):
    manager_id = request.session.get('manager_id')
    if manager_id:
        try:
            manager = Manager.objects.get(id=manager_id)
            if manager.role == 'manager':
                trainer = get_object_or_404(Trainer, id=trainer_id, manager=manager)
                trainer.delete()
                messages.success(request, 'Trainer deleted successfully!')
                return redirect('view_trainers')

            else:
                messages.error(request, 'You must be logged in as a manager to delete trainers.')
                return redirect('manager_login')
        except Manager.DoesNotExist:
            messages.error(request, 'Manager not found. Please log in again.')
            return redirect('manager_login')
    else:
        messages.error(request, 'Please log in first.')
        return redirect('manager_login')


def manager_logout(request):
    if 'manager_id' in request.session:
        request.session.pop('manager_id', None)
        messages.success(request, 'You have been logged out successfully.')
    else:
        messages.error(request, 'No active session found.')
    return redirect('manager_login')

def trainer_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        employee_id = request.POST.get('employee_id').lower()

        try:
            trainer = Trainer.objects.get(email=email, employee_id=employee_id)

            if trainer.role == 'Trainer' and trainer.status == 1:
                # Add course-specific condition if needed
                if trainer.course == 'Python Programming':
                    # Store the trainer's id in the session
                    request.session['trainer_id'] = trainer.id
                    return redirect('trainer_dashboard')
                elif trainer.course == 'Java Programming':
                    # Logic for other courses
                    request.session['trainer_id'] = trainer.id
                    return redirect('trainer_dashboard')
                elif trainer.course == 'Data Science':
                    # Logic for other courses
                    request.session['trainer_id'] = trainer.id
                    return redirect('trainer_dashboard')
                elif trainer.course == 'Data Analytics':
                    # Logic for other courses
                    request.session['trainer_id'] = trainer.id
                    return redirect('trainer_dashboard')
                elif trainer.course == 'DevOps cum AWS':
                    # Logic for other courses
                    request.session['trainer_id'] = trainer.id
                    return redirect('trainer_dashboard')
                elif trainer.course == 'Cyber Security':
                    # Logic for other courses
                    request.session['trainer_id'] = trainer.id
                    return redirect('trainer_dashboard')
                elif trainer.course == 'Communication':
                    # Logic for other courses
                    request.session['trainer_id'] = trainer.id
                    return redirect('trainer_dashboard')
                elif trainer.course == 'Aptitude':
                    # Logic for other courses
                    request.session['trainer_id'] = trainer.id
                    return redirect('trainer_dashboard')

                else:
                    messages.error(request, 'You are not assigned to the correct course to log in.')
                    return redirect('trainer_login')
            else:
                messages.error(request, 'Invalid credentials or inactive trainer.')
                return redirect('trainer_login')
        except Trainer.DoesNotExist:
            messages.error(request, 'Trainer not found or invalid credentials.')
            return redirect('trainer_login')

    return render(request, 'trainer/trainer_login.html')

def trainer_dashboard(request):
    trainer_id = request.session.get('trainer_id')

    if trainer_id:
        try:
            trainer = Trainer.objects.get(id=trainer_id)

            if trainer.status == 1:
                students_count = Kapil_Student.objects.filter(course=trainer.course).count()
                assessments_count = AssessmentDetails.objects.filter(trainer=trainer).count()
                return render(request, 'trainer/trainer_dashboard.html', {
                    'trainer': trainer,
                    'students_count': students_count,
                    'assessments_count': assessments_count
                })
            else:
                messages.error(request, 'Your account is inactive.')
                return redirect('trainer_login')

        except Trainer.DoesNotExist:
            messages.error(request, 'Trainer not found or invalid credentials.')
            return redirect('trainer_login')
    else:
        messages.error(request, 'Please log in first.')
        return redirect('trainer_login')



def add_assessment(request):
    trainer_id = request.session.get('trainer_id')

    if trainer_id:
        try:
            trainer = Trainer.objects.get(id=trainer_id)
            course = trainer.course  # Get the trainer's course
            created_by = trainer.name

            if request.method == 'POST':
                assessment_type = request.POST.get('assessment_type')

                # Initialize number_of_questions, number_of_mcq, and number_of_programs
                number_of_mcq = 0
                number_of_programs = 0

                # Validate based on assessment type
                if assessment_type == 'MCQ':
                    number_of_questions = request.POST.get('number_of_questions', '0')  # Default to '0' if empty

                    if not number_of_questions.isdigit():
                        messages.error(request, "Please enter a valid number of MCQ questions.")
                        return redirect('add_assessment')
                    
                    number_of_questions = int(number_of_questions)

                elif assessment_type == 'Program':
                    number_of_questions = request.POST.get('number_of_questions', '0')  # Default to '0' if empty

                    if not number_of_questions.isdigit():
                        messages.error(request, "Please enter a valid number of Program questions.")
                        return redirect('add_assessment')
                    number_of_questions = int(number_of_questions)

                elif assessment_type == 'Both':
                    number_of_mcq_str = request.POST.get('number_of_mcq', '0')
                    number_of_programs_str = request.POST.get('number_of_programs', '0')

                    if not number_of_mcq_str.isdigit() or not number_of_programs_str.isdigit():
                        messages.error(request, "Please enter valid numbers for MCQ and Program questions.")
                        return redirect('add_assessment')
                    number_of_mcq = int(number_of_mcq_str)
                    number_of_programs = int(number_of_programs_str)
                    number_of_questions = number_of_mcq + number_of_programs

                # Generate the next assessment name while avoiding duplicates
                base_assessment_name = f'{course} - '
                next_number = 1  # Start with 1 if no assessment exists
                while True:
                    assessment_name = f'{base_assessment_name}{next_number}'
                    if not AssessmentDetails.objects.filter(assessment_name=assessment_name).exists():
                        break  # If the assessment name doesn't exist, break out of the loop
                    next_number += 1  # Otherwise, increment the number and check again

                # Create new assessment object
                new_assessment = AssessmentDetails(
                    manager=trainer.manager,  # Assuming each trainer has a related manager
                    trainer=trainer,
                    assessment_type=assessment_type,
                    number_of_questions=number_of_questions,
                    number_of_mcq=number_of_mcq,
                    number_of_programs=number_of_programs,
                    assessment_name=assessment_name,
                    created_by=created_by,
                    added_on=now(),
                    status=True
                )
                new_assessment.save()
                messages.success(request, f'Assessment "{assessment_name}" added successfully!')
                return redirect('view_assessment')

            # Generate the next assessment name to display for the form
            base_assessment_name = f'{course} - '
            next_number = 1
            while True:
                assessment_name = f'{base_assessment_name}{next_number}'
                if not AssessmentDetails.objects.filter(assessment_name=assessment_name).exists():
                    break
                next_number += 1

            return render(request, 'trainer/add_assessment.html', {
                'trainer': trainer,
                'next_assessment_number': assessment_name,
            })

        except Trainer.DoesNotExist:
            messages.error(request, 'Trainer not found or invalid credentials.')
            return redirect('trainer_login')
    else:
        messages.error(request, 'Please log in first.')
        return redirect('trainer_login')


def edit_assessment(request, assessment_id):
    trainer_id = request.session.get('trainer_id')

    if not trainer_id:
        messages.error(request, 'Please log in first.')
        return redirect('trainer_login')

    # Fetch the assessment to edit
    assessment = get_object_or_404(AssessmentDetails, id=assessment_id, trainer_id=trainer_id)

    if request.method == 'POST':
        assessment_type = request.POST.get('assessment_type')

        # Reset question numbers
        number_of_mcq = 0
        number_of_programs = 0
        number_of_questions = 0

        # Validate and process number of questions based on assessment type
        if assessment_type == 'MCQ':
            number_of_questions = request.POST.get('number_of_questions', '0')
            if not number_of_questions.isdigit():
                messages.error(request, "Please enter a valid number of MCQ questions.")
                return redirect('edit_assessment', assessment_id=assessment_id)
            number_of_questions = int(number_of_questions)
            

        elif assessment_type == 'Program':
            number_of_questions = request.POST.get('number_of_questions', '0')
            if not number_of_questions.isdigit():
                messages.error(request, "Please enter a valid number of Program questions.")
                return redirect('edit_assessment', assessment_id=assessment_id)
            number_of_questions = int(number_of_questions)
            

        elif assessment_type == 'Both':
            number_of_mcq_str = request.POST.get('number_of_mcq', '0')
            number_of_programs_str = request.POST.get('number_of_programs', '0')

            if not number_of_mcq_str.isdigit() or not number_of_programs_str.isdigit():
                messages.error(request, "Please enter valid numbers for MCQ and Program questions.")
                return redirect('edit_assessment', assessment_id=assessment_id)

            number_of_mcq = int(number_of_mcq_str)
            number_of_programs = int(number_of_programs_str)
            number_of_questions = number_of_mcq + number_of_programs

        # Update assessment details
        assessment.assessment_type = assessment_type
        assessment.number_of_questions = number_of_questions
        assessment.number_of_mcq = number_of_mcq
        assessment.number_of_programs = number_of_programs
        assessment.save()

        messages.success(request, f'Assessment "{assessment.assessment_name}" updated successfully!')
        return redirect('view_assessment')

    return render(request, 'trainer/edit_assessment.html', {
        'assessment': assessment,
    })

def delete_assessment(request, assessment_id):
    trainer_id = request.session.get('trainer_id')

    if not trainer_id:
        messages.error(request, 'Please log in first.')
        return redirect('trainer_login')

    # Fetch the assessment to delete
    assessment = get_object_or_404(AssessmentDetails, id=assessment_id, trainer_id=trainer_id)

    # Delete the assessment
    assessment_name = assessment.assessment_name
    assessment.delete()

    messages.success(request, f'Assessment "{assessment_name}" deleted successfully!')
    return redirect('view_assessment')


def add_assessment_paper(request, assessment_id):
    trainer_id = request.session.get('trainer_id')

    if trainer_id:
        try:
            # Fetch the trainer and assessment details
            trainer = Trainer.objects.get(id=trainer_id)
            assessment = AssessmentDetails.objects.get(id=assessment_id, trainer=trainer)
            assessment_questions = range(1, assessment.number_of_questions + 1)

            if request.method == 'POST':
                # Get the form data
                assessment_date = request.POST.get('assessment_date')
                assessment_duration = request.POST.get('assessment_duration')
                questions_data = []
                question_files = []

                # Loop through the number of questions and gather the data
                for i in range(1, assessment.number_of_questions + 1):
                    question_text = request.POST.get(f'question_{i}')
                    option_a = request.POST.get(f'option_a_{i}')
                    option_b = request.POST.get(f'option_b_{i}')
                    option_c = request.POST.get(f'option_c_{i}')
                    option_d = request.POST.get(f'option_d_{i}')
                    answer = request.POST.get(f'answer_{i}')

                    # Ensure all question data is provided
                    if not all([question_text, option_a, option_b, option_c, option_d, answer]):
                        messages.error(request, f'Please fill in all fields for question {i}.')
                        return redirect('add_assessment_paper', assessment_id=assessment_id)

                    questions_data.append({
                        'question_text': question_text,
                        'option_a': option_a,
                        'option_b': option_b,
                        'option_c': option_c,
                        'option_d': option_d,
                        'answer': answer,
                    })

                    # Handle file uploads (if any)
                    file_field = request.FILES.get(f'file_{i}')
                    if file_field:
                        # Create a folder path inside static/images/assessment_name
                        assessment_folder = f'images/{assessment.assessment_name.replace(" ", "_")}'
                        folder_path = os.path.join(settings.BASE_DIR, 'static', assessment_folder)  # Save in static folder
                        if not os.path.exists(folder_path):
                            os.makedirs(folder_path)  # Create the folder if it doesn't exist

                        # Save the file in the folder
                        file_system = FileSystemStorage(location=folder_path)
                        filename = file_system.save(file_field.name, file_field)

                        # Save relative path to the database in the format static/images/assessment_name/filename
                        file_path = os.path.join(assessment_folder, filename).replace("\\", "/")  # Normalize path to use forward slashes
                        question_files.append(file_path)
                    else:
                        question_files.append(None)  # No file uploaded for this question

                # Create the new assessment paper
                new_assessment_paper = AssessmentPaper(
                    manager=trainer.manager,
                    trainer=trainer,
                    assessment=assessment,
                    assessment_date=assessment_date,
                    assessment_duration=assessment_duration,
                    questions=questions_data,  # Save questions as JSON
                    question_files=question_files,  # Save file paths as JSON
                    course_name=trainer.course,
                    assessment_name=assessment.assessment_name,
                    created_by=trainer.name,
                    added_on=now(),
                    status=True,  # Assuming status is True by default
                )
                new_assessment_paper.save()

                # Update paper_added_status in AssessmentDetails
                assessment.paper_added_status = 1  # Assuming this field exists
                assessment.save()  # Don't forget to save the updated assessment

                messages.success(request, f'Assessment Paper for "{assessment.assessment_name}" added successfully!')
                return redirect('view_assessment_paper')  # Adjust the redirect as needed

            return render(request, 'trainer/add_assessment_paper.html', {
                'trainer': trainer,
                'assessment': assessment,
                'assessment_questions': assessment_questions
            })

        except Trainer.DoesNotExist:
            messages.error(request, 'Trainer not found or invalid credentials.')
            return redirect('trainer_login')
        except AssessmentDetails.DoesNotExist:
            messages.error(request, 'Selected assessment not found.')
            return redirect('add_assessment_paper')
    else:
        messages.error(request, 'Please log in first.')
        return redirect('trainer_login')
def view_assessment_paper(request, assessment_id):
    trainer_id = request.session.get('trainer_id')

    if trainer_id:
        try:
            # Get the logged-in trainer
            trainer = Trainer.objects.get(id=trainer_id)

            if trainer.status == 1:  # Check if the trainer account is active
                try:
                    # Get the assessment details
                    assessment = AssessmentDetails.objects.get(id=assessment_id, trainer=trainer, paper_added_status=1)

                    # Get the paper details for the assessment (use filter to handle multiple entries)
                    assessment_papers = AssessmentPaper.objects.filter(assessment=assessment)

                    if assessment_papers.exists():
                        # If there are multiple papers, you can either choose the first one or handle it differently
                        assessment_paper = assessment_papers.first()  # For now, selecting the first one
                        
                        # Prepare the details for rendering
                        assessment_details = {
                            'assessment_name': assessment_paper.assessment_name,
                            'assessment_date': assessment_paper.assessment_date,
                            'assessment_duration': assessment_paper.assessment_duration,
                            'course_name': assessment_paper.course_name,
                            'created_by': assessment_paper.created_by,
                            'added_on': assessment_paper.added_on,
                            'questions': assessment_paper.questions,
                            'question_files': assessment_paper.question_files,
                            'status': assessment_paper.status,
                        }
                        print(assessment_details)

                        # Render the details to the template
                        return render(request, 'trainer/view_assessment_paper.html', {
                            'trainer': trainer,
                            'assessment_details': assessment_details,
                        })

                    else:
                        messages.error(request, "No paper found for this assessment.")
                        return redirect('trainer_dashboard')

                except AssessmentDetails.DoesNotExist:
                    messages.error(request, "No matching assessment found.")
                    return redirect('trainer_dashboard')

            else:
                messages.error(request, "Your account is inactive. Please contact the admin.")
                return redirect('trainer_dashboard')

        except Trainer.DoesNotExist:
            messages.error(request, 'Trainer not found or invalid credentials.')
            return redirect('trainer_login')

    else:
        messages.error(request, 'Please log in first.')
        return redirect('trainer_login')

    
    # if trainer_id:
    #     try:
    #         trainer = Trainer.objects.get(id=trainer_id)

    #         if trainer.status == 1:  # Only display if the trainer's status is 1
    #             # Fetch the assessment paper based on the assessment_id
    #             assessment_paper = get_object_or_404(AssessmentPaper, id=assessment_id, trainer=trainer)

    #             # Get questions and files for the paper
    #             questions = assessment_paper.questions  # This will be a list of dictionaries
    #             question_files = assessment_paper.question_files  # List of file paths, or None

    #             # Prepare data for display
    #             assessment_details = {
    #                 'assessment_name': assessment_paper.assessment_name,
    #                 'assessment_date': assessment_paper.assessment_date,
    #                 'assessment_duration': assessment_paper.assessment_duration,
    #                 'course_name': assessment_paper.course_name,
    #                 'created_by': assessment_paper.created_by,
    #                 'added_on': assessment_paper.added_on,
    #                 'questions': questions,
    #                 'question_files': question_files,
    #                 'status': assessment_paper.status,
    #             }

    #             return render(request, 'trainer/view_assessment_paper.html', {
    #                 'trainer': trainer,
    #                 'assessment_details': assessment_details,
    #                 'assessment_id': assessment_id
    #             })
    #         else:
    #             messages.error(request, "Your account is inactive. Please contact the admin.")
    #             return redirect('trainer_dashboard')
        
    #     except Trainer.DoesNotExist:
    #         messages.error(request, 'Trainer not found or invalid credentials.')
    #         return redirect('trainer_login')

    # else:
    #     messages.error(request, 'Please log in first.')
    #     return redirect('trainer_login')


def view_assessment(request):
    trainer_id = request.session.get('trainer_id')
    if trainer_id:
        try:
            trainer = Trainer.objects.get(id=trainer_id)
            if trainer.status == 1:
                assessments = AssessmentDetails.objects.filter(trainer=trainer).order_by('-added_on')

                return render(request, 'trainer/view_assessment.html', {
                    'trainer': trainer,
                    'assessments': assessments
                })
            else:
                messages.error(request, 'Your account is inactive.')
                return redirect('trainer_login')

        except Trainer.DoesNotExist:
            messages.error(request, 'Trainer not found or invalid credentials.')
            return redirect('trainer_login')
    else:
        messages.error(request, 'Please log in first.')
        return redirect('trainer_login')



def trainer_logout(request):
    if 'trainer_id' in request.session:
        request.session.pop('trainer_id', None)
        messages.success(request, 'You have been logged out successfully.')
    else:
        messages.error(request, 'No active session found.')
    return redirect('trainer_login')



def validate_password(password, email=None ,mobile=None):
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not any(char.isdigit() for char in password):
        return "Password must contain at least one digit."
    if not any(char.isupper() for char in password):
        return "Password must contain at least one uppercase letter."
    if not any(char.islower() for char in password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special character."
    if password == email or password == mobile:
        return "Password should not be the same as email or mobile number."
    return None  

def validate_mobile(mobile):
    if not re.match(r"^[0-9]{10}$", mobile):
        return "Mobile number must be exactly 10 digits."
    return None  

#kapil-signup

def delete_otp_after_delay_kapil(student_id):
    """Deletes OTP from student record after 5 minutes."""
    try:
        student = Kapil_Student.objects.get(id=student_id)
        student.otp = None
        student.verification_reset_link=None
        student.save()
    except Kapil_Student.DoesNotExist:
        pass


@csrf_exempt
def kapil_signup_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode("utf-8"))

            # Check if enrollment ID (used as email here) already exists
            if Kapil_Student.objects.filter(enrollment_id=data['enrollment_id']).exists():
                return JsonResponse({"message": "Enrollment ID already exists.", "status_code": 400}, status=400)
            
            manager=Manager.objects.order_by('id').first()
            if not manager:
                return JsonResponse({"message":"No manager found.","status_code":404},status=404)

            # Save student
            verification_reset_link  = str(uuid.uuid4())  # Generate unique verification token
            otp_code = str(random.randint(100000, 999999))  # Generate 6-digit OTP

            kapil_student = Kapil_Student(
                manager=manager,
                student_name=data['student_name'],
                enrollment_id=data['enrollment_id'],  # Used as email identifier
                mobile=data['mobile'],
                email=data['email'],
                password=data['password'],
                confirm_password=data['confirm_password'],
                course=data['course'],
                otp=otp_code,
                verification_reset_link =verification_reset_link ,
            )
            kapil_student.clean()
            kapil_student.save()

            # Start a background thread to delete OTP after 5 minutes
            threading.Timer(300, delete_otp_after_delay_kapil, args=[kapil_student.id]).start()

            # Send OTP via email
            email_subject = "Kapil IT Skill Hub - OTP Verification"
            email_message = f"""
            Hello {kapil_student.student_name},

            Your OTP for verification is: {otp_code}
            This OTP is valid for 5 minutes.

            Please verify your email by entering this OTP in the verification form.

            Regards,
            Kapil LMS Team
            """

            send_mail(
                subject=email_subject,
                message=email_message,
                from_email="srinikethan2413@gmail.com",
                recipient_list=[kapil_student.email],  
                fail_silently=False,
            )

            

            return JsonResponse({
                "message": "Registered successfully. OTP sent to your email.",
                "id": kapil_student.id,
                "verification_reset_link": str(kapil_student.verification_reset_link),  # ✅ Now it's a string
                "enrollment_id": kapil_student.enrollment_id,
                "status_code": 201
            }, status=201)
        
        
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON data in the request body.", "status_code": 400}, status=400)
        #except IntegrityError:
        #    return JsonResponse({"message": "Database integrity error.", "status_code": 500}, status=500)
        except Exception as e:
            return JsonResponse({"message": f"An unexpected error occurred: {str(e)}", "status_code": 500}, status=500)

    return JsonResponse({"message": "Invalid HTTP method. Only POST is allowed.", "status_code": 405},status=405)


#resend otp kapil

def resend_otp_after_expiry(student):
    """Resends OTP if not verified within 5 minutes."""
    import time
    time.sleep(300)  # Wait for 5 minutes

    # Fetch the latest OTP expiry time
    student.refresh_from_db()
    if student.otp and student.otp_expiry and datetime.now() > student.otp_expiry:
        student.set_new_otp()  # Generate new OTP and update expiry

        email_subject = "Kapil IT Skill Hub - OTP Resent"
        email_message = f"""
        Hello {student.student_name},

        Your new OTP for verification is: {student.otp}
        This OTP is valid for 5 minutes.

        Regards,
        Kapil LMS Team
        """

        send_mail(
            subject=email_subject,
            message=email_message,
            from_email="srinikethan2413@gmail.com",
            recipient_list=[student.email],
            fail_silently=False,
        )

        print(f"New OTP {student.otp} sent to {student.email} after expiry.")


@csrf_exempt
def kapil_resend_otp_view(request):
    if request.method == 'POST':
        try:
            print("Request received for OTP resend.")
            data = json.loads(request.body.decode("utf-8"))
            enrollment_id = data.get('enrollment_id') 
            email = data.get('email')
            
            # Check if student exists
            if not Kapil_Student.objects.filter(enrollment_id=enrollment_id,email=email).exists():
                return JsonResponse({"message": "Student not found.", "status_code": 404}, status=404)

            kapil_student = Kapil_Student.objects.get(enrollment_id=enrollment_id, email=email)
            

            # Generate new OTP
            verification_reset_link  = uuid.uuid4()
            new_otp = str(random.randint(100000, 999999))
            kapil_student.otp = new_otp
            kapil_student.verification_reset_link = verification_reset_link
            kapil_student.save()

            print(f"Resent OTP: {new_otp} to {kapil_student.email}")

            # Restart the 5-minute timer
            threading.Timer(300, delete_otp_after_delay_kapil, args=[kapil_student.id]).start()

            # Send OTP via email
            email_subject = "Kapil IT Skill Hub - OTP Resend"
            email_message = f"""
            Hello {kapil_student.student_name},

            Your new OTP for verification is: {new_otp}
            This OTP is valid for 5 minutes.

            Please enter this OTP in the verification form.

            Regards,
            Kapil LMS Team
            """

            send_mail(
                subject=email_subject,
                message=email_message,
                from_email="srinikethan2413@gmail.com",
                recipient_list=[kapil_student.email],
                fail_silently=False,
            )

            return JsonResponse({
                "message": "OTP resent successfully.",
                "status_code": 200,
                "verification_reset_link": str(kapil_student.verification_reset_link),
                "email": kapil_student.email,
                "enrollment_id": kapil_student.enrollment_id,
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON data.", "status_code": 400}, status=400)
        except Kapil_Student.DoesNotExist:
            return JsonResponse({"message": "Student not found.", "status_code": 404}, status=404)
        except Exception as e:
            return JsonResponse({"message": f"An unexpected error occurred: {str(e)}", "status_code": 500}, status=500)

    return JsonResponse({"message": "Invalid HTTP method. Only POST is allowed.", "status_code": 405}, status=405)


@csrf_exempt
def verify_kapil_student(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            otp = str(data.get('otp')).strip()
            verification_reset_link = str(data.get('verification_reset_link')).strip()

            if not email or not otp or not verification_reset_link:
                return JsonResponse({"message": "Email, OTP, and verification link are required.", "status_code": 400}, status=400)

            # Fetch the student using both email and verification link
            student = Kapil_Student.objects.filter(
                email=email,
                verification_reset_link__isnull=False
            ).first()

            if not student:
                return JsonResponse({"error": "Student not found or verification link expired"}, status=404)

            # Clean and compare
            stored_otp = str(student.otp).strip() if student.otp else ""
            stored_link = str(student.verification_reset_link).strip() if student.verification_reset_link else ""

            print(f"Received OTP: '{otp}', Stored OTP: '{stored_otp}'")
            print(f"Received Link: '{verification_reset_link}', Stored Link: '{stored_link}'")

            if stored_otp != otp:
                return JsonResponse({"error": "Invalid OTP"}, status=400)

            if stored_link != verification_reset_link:
                return JsonResponse({"error": "Invalid verification link"}, status=400)

            
            student.otp = None
            student.verification_reset_link = None
            student.save()

            return JsonResponse({"message": "Verification successful.",
                                  "status_code": 200,
                                   "student_id": student.id
                                  }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON data.", "status_code": 400}, status=400)
        except Exception as e:
            return JsonResponse({"message": f"An unexpected error occurred: {str(e)}", "status_code": 500}, status=500)

    return JsonResponse({"message": "Invalid HTTP method. Only POST is allowed.", "status_code": 405}, status=405)


@csrf_exempt
def kapil_reset_password_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode("utf-8"))
            email = data.get('email')   
            # otp = data.get('otp')
            new_password = data.get('new_password')
            confirm_password = data.get('confirm_password')

            if new_password != confirm_password:
                return JsonResponse({"message": "Passwords do not match.", "status_code": 400}, status=400)

            kapil_student = Kapil_Student.objects.filter(email=email).first()
            if not kapil_student:
                return JsonResponse({"message": "User not found.", "status_code": 404}, status=404)

            # if str(kapil_student.otp) != str(otp):
            #     return JsonResponse({"message": "Invalid OTP.", "status_code": 400}, status=400)

            # Save the hashed password (for security)
            # kapil_student.password = make_password(new_password)
            # kapil_student.confirm_password = make_password(confirm_password)
            kapil_student.password =  new_password
            kapil_student.confirm_password = confirm_password
            kapil_student.otp = None  # Clear OTP after use
            kapil_student.save()

            return JsonResponse({"message": "Password reset successful.", "status_code": 200}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON data.", "status_code": 400}, status=400)
        except Exception as e:
            return JsonResponse({"message": f"An error occurred: {str(e)}", "status_code": 500}, status=500)

    return JsonResponse({"message": "Invalid HTTP method. Only POST is allowed.", "status_code": 405}, status=405)


@csrf_exempt
def kapil_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            enrollment_id = data.get('enrollment_id')
            password = data.get('password')

            if not enrollment_id or not password:
                return JsonResponse({"message": "Enrollment ID and password are required.", "status_code": 400}, status=400)

            user = Kapil_Student.objects.filter(enrollment_id=enrollment_id, password=password).first()

            if user:
                return JsonResponse({
                    "message": "Login successful",
                    "student_id": user.id,
                    "trainer_selected": user.trainer_selected,  # ✅ Include this line
                    "status_code": 200
                }, status=200)
            else:
                return JsonResponse({"message": "Invalid enrollment ID or password.", "status_code": 401}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON data in the request body.", "status_code": 400}, status=400)
        except Exception as e:
            return JsonResponse({"message": f"An unexpected error occurred: {str(e)}", "status_code": 500}, status=500)

    return JsonResponse({"message": "Invalid HTTP method. Only POST is allowed.", "status_code": 405}, status=405)



#nonkapil-signup

def delete_otp_after_delay_non_kapil(student_id):
    """Deletes OTP from student record after 5 minutes."""
    try:
        student = Non_kapil_student.objects.get(id=student_id)
        student.Otp = None
        student.Verification_reset_link= None
        student.save()
    except Non_kapil_student.DoesNotExist:
        pass


@csrf_exempt
def non_kapil_signup_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode("utf-8"))

            # Validate password
            password_error = validate_password(data['password'], data['email'], data['mobile'])
            if password_error:
                return JsonResponse({"message": password_error, "status_code": 400}, status=400)

            # Validate mobile
            mobile_error = validate_mobile(data['mobile'])
            if mobile_error:
                return JsonResponse({"message": mobile_error, "status_code": 400}, status=400)

            # Check if email or mobile already exists
            if Non_kapil_student.objects.filter(Email=data['email']).exists():
                return JsonResponse({"message": "Email already exists.", "status_code": 400}, status=400)

            if Non_kapil_student.objects.filter(Mobile=data['mobile']).exists():
                return JsonResponse({"message": "Mobile number already exists.", "status_code": 400}, status=400)

            # Save student
            verification_reset_link  = str(uuid.uuid4())  # Generate unique verification verification_reset_link
            otp_code = str(random.randint(100000, 999999))  # Generate 6-digit OTP

            non_kapil_student = Non_kapil_student(
                Student_name=data['student_name'],
                Qualification=data['qualification'],
                Branch=data['branch'],
                College_name=data['college_name'],
                Current_year=data['current_year'],
                Mobile=data['mobile'],
                Email=data['email'],
                Password=data['password'],
                Confirm_password=data['confirm_password'],
                Course=data['course'],
                Otp=otp_code,
                Verification_reset_link=verification_reset_link ,
            )
            non_kapil_student.clean()
            non_kapil_student.save()

            # Start a background thread to delete OTP after 5 minutes
            threading.Timer(300, delete_otp_after_delay_non_kapil, args=[non_kapil_student.id]).start()

            # Send OTP via email
            email_subject = "Kapil IT Skill Hub - OTP Verification"
            email_message = f"""
            Hello {non_kapil_student.Student_name},

            Your OTP for verification is: {otp_code}
            This OTP is valid for 5 minutes.

            Please verify your email by entering this OTP in the verification form.

            Regards,
            Kapil LMS Team
            """

            send_mail(
                subject=email_subject,
                message=email_message,
                from_email="srinikethan2413@gmail.com",
                recipient_list=[non_kapil_student.Email],
                fail_silently=False,
            )

            return JsonResponse({
                "message": "Registered successfully. OTP sent to your email.",
                "id": non_kapil_student.id,
                "status_code": 201
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON data in the request body.", "status_code": 400}, status=400)
        # except IntegrityError:
            # return JsonResponse({"message": "Database integrity error.", "status_code": 500}, status=500)
        except Exception as e:
            return JsonResponse({"message": f"An unexpected error occurred: {str(e)}", "status_code": 500}, status=500)

    return JsonResponse({"message": "Invalid HTTP method. Only POST is allowed.", "status_code": 405},status=405)



#resend otp non-kapil

def resend_otp_after_expiry(student):
    """Resends OTP if not verified within 5 minutes."""
    import time
    time.sleep(300)  # Wait for 5 minutes

    # Fetch the latest OTP expiry time
    student.refresh_from_db()
    if student.otp and student.otp_expiry and datetime.now() > student.otp_expiry:
        student.set_new_otp()  # Generate new OTP and update expiry

        email_subject = "Kapil IT Skill Hub - OTP Resent"
        email_message = f"""
        Hello {student.student_name},

        Your new OTP for verification is: {student.otp}
        This OTP is valid for 5 minutes.

        Regards,
        Kapil LMS Team
        """

        send_mail(
            subject=email_subject,
            message=email_message,
            from_email="srinikethan2413@gmail.com",
            recipient_list=[student.email],
            fail_silently=False,
        )

        print(f"New OTP {student.otp} sent to {student.email} after expiry.")


@csrf_exempt
def non_kapil_resend_otp_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode("utf-8"))
            email = data.get('email')

            # Check if student exists
            if not Non_kapil_student.objects.filter(Email=email).exists():
                return JsonResponse({"message": "Student not found.", "status_code": 404}, status=404)

            non_kapil_student = Non_kapil_student.objects.get(Email=email)

            # Generate new OTP
            verification_reset_link = uuid.uuid4()
            new_otp = str(random.randint(100000, 999999))
            non_kapil_student.Otp = new_otp
            non_kapil_student.Verification_reset_link = verification_reset_link
            non_kapil_student.save()

            print(f"Resent OTP: {new_otp}")

            # Restart the 5-minute timer
            threading.Timer(300, delete_otp_after_delay_non_kapil, args=[non_kapil_student.id]).start()

            # Send OTP via email
            email_subject = "Kapil IT Skill Hub - OTP Resend"
            email_message = f"""
            Hello {non_kapil_student.Student_name},

            Your new OTP for verification is: {new_otp}
            This OTP is valid for 5 minutes.

            Please enter this OTP in the verification form.

            Regards,
            Kapil LMS Team
            """

            send_mail(
                subject=email_subject,
                message=email_message,
                from_email="srinikethan2413@gmail.com",
                recipient_list=[non_kapil_student.Email],
                fail_silently=False,
            )

            return JsonResponse({
                "message": "OTP resent successfully.",
                "status_code": 200
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON data.", "status_code": 400}, status=400)
        except Non_kapil_student.DoesNotExist:
            return JsonResponse({"message": "Student not found.", "status_code": 404}, status=404)
        except Exception as e:
            return JsonResponse({"message": f"An unexpected error occurred: {str(e)}", "status_code": 500}, status=500)

    return JsonResponse({"message": "Invalid HTTP method. Only POST is allowed.", "status_code": 405}, status=405)



@csrf_exempt
def verify_non_kapil_student(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            otp = data.get('otp')
            verification_reset_link = data.get('verification_reset_link')

            if not email or not otp or not verification_reset_link:
                return JsonResponse({"message": "Enrollment ID, OTP, and verification link are required.", "status_code": 400}, status=400)

            # Fetch the student
            student = get_object_or_404(Non_kapil_student, Email=email)

            # Debug: Print stored vs received values
            print(f"Received OTP: {otp}, Stored OTP: {student.Otp}")
            print(f"Received Verification Link: {verification_reset_link}, Stored Verification Link: {student.Verification_reset_link}")

            # Convert the received verification link to UUID before comparing
            try:
                provided_link = uuid.UUID(verification_reset_link.strip())  # Convert string to UUID
            except ValueError:
                return JsonResponse({"message": "Invalid UUID format for verification link.", "status_code": 400}, status=400)

            # Check if OTP and verification link match
            if str(student.Otp).strip() == str(otp).strip() and student.Verification_reset_link == provided_link:
                student.Otp = None  # Clear OTP after successful verification
                student.Verification_reset_link = None  # Clear verification link after successful verification
                student.save()

                return JsonResponse({"message": "Verification successful.", "status_code": 200}, status=200)
            else:
                return JsonResponse({"message": "Invalid OTP or verification link.", "status_code": 400}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON data.", "status_code": 400}, status=400)
        except Exception as e:
            return JsonResponse({"message": f"An unexpected error occurred: {str(e)}", "status_code": 500}, status=500)

    return JsonResponse({"message": "Invalid HTTP method. Only POST is allowed.", "status_code": 405}, status=405)



#forgot password
@csrf_exempt
def non_kapil_reset_password_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode("utf-8"))
            email = data.get('email')   
            otp = data.get('otp')
            new_password = data.get('new_password')
            confirm_password = data.get('confirm_password')

            # Validate password confirmation
            if new_password != confirm_password:
                return JsonResponse({"message": "Passwords do not match.", "status_code": 400}, status=400)

            # Check if user exists
            non_kapil_student = Non_kapil_student.objects.filter(Email=email).first()
            if not non_kapil_student:
                return JsonResponse({"message": "User not found.", "status_code": 404}, status=404)

            # Validate OTP
            if non_kapil_student.Otp != otp:
                return JsonResponse({"message": "Invalid OTP.", "status_code": 400}, status=400)

            # Update password
            non_kapil_student.Password = new_password
            non_kapil_student.Confirm_password = confirm_password
            non_kapil_student.Otp = None  # Clear OTP after use
            non_kapil_student.save()

            return JsonResponse({"message": "Password reset successful.", "status_code": 200}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON data.", "status_code": 400}, status=400)
        except Exception as e:
            return JsonResponse({"message": f"An error occurred: {str(e)}", "status_code": 500}, status=500)

    return JsonResponse({"message": "Invalid HTTP method. Only POST is allowed.", "status_code": 405}, status=405)


@csrf_exempt
def get_course_by_enrollment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        enrollment_id = data.get('enrollment_id')

        try:
            student = Kapil_Student.objects.get(enrollment_id=enrollment_id)
            return JsonResponse({'course': student.course}, status=200)
        except Kapil_Student.DoesNotExist:
            return JsonResponse({'message': 'Student not found'}, status=404)
    
    return JsonResponse({'message': 'Invalid request method'}, status=400)


@csrf_exempt
def get_course_trainers(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            student_id = data.get('student_id')

            if not student_id:
                return JsonResponse({
                    "message": "Student ID is required.",
                    "status_code": 400
                }, status=400)

            student = Kapil_Student.objects.get(id=student_id)
            course_name = student.course

            # Define course-specific subjects
            course_subject_map = {
                "Python Full Stack": ["Python Programming", "Frontend", "SQL"],
                "Java Full Stack": ["Java Programming", "Frontend", "SQL"],
                "Data Analytics": ["Excel", "SQL", "Power BI"],
                # Add more courses if needed
            }

            # Get the subjects based on student's course
            subjects_for_course = course_subject_map.get(course_name, [])

            # Fetch trainers who teach in this course
            trainers = Trainer.objects.filter(course=course_name, status=1)

            course_data = {}

            for subject in subjects_for_course:
                trainer_names = trainers.filter(subjects__contains=[subject]).values_list('name', flat=True)
                course_data[subject] = {
                    "label": subject,
                    "options": list(trainer_names)
                }

            return JsonResponse({
                "course": course_name,
                "subjects": course_data,
                "status_code": 200
            })

        except Kapil_Student.DoesNotExist:
            return JsonResponse({
                "message": "Student not found.",
                "status_code": 404
            }, status=404)

        except json.JSONDecodeError:
            return JsonResponse({
                "message": "Invalid JSON format.",
                "status_code": 400
            }, status=400)

        except Exception as e:
            return JsonResponse({
                "message": f"Unexpected error: {str(e)}",
                "status_code": 500
            }, status=500)

    return JsonResponse({
        "message": "Only POST method allowed.",
        "status_code": 405
    }, status=405)


@csrf_exempt
def submit_selected_trainers(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_id = data.get('student_id')
            selected_trainers = data.get('selected_trainers', {})

            if not student_id:
                return JsonResponse({"message": "Student ID is required", "status_code": 400}, status=400)

            student = Kapil_Student.objects.get(id=student_id)

            # You can save selected trainers here if needed (e.g., in a JSONField)

            student.trainer_selected = True
            student.save()

            return JsonResponse({"message": "Trainer selection submitted successfully", "status_code": 200}, status=200)

        except Kapil_Student.DoesNotExist:
            return JsonResponse({"message": "Student not found", "status_code": 404}, status=404)

        except Exception as e:
            return JsonResponse({"message": f"Unexpected error: {str(e)}", "status_code": 500}, status=500)

    return JsonResponse({"message": "Only POST method allowed", "status_code": 405}, status=405)
