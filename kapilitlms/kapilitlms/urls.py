"""
URL configuration for kapilitlms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from lmsapp .views import (kapil_signup_view, non_kapil_signup_view, kapil_resend_otp_view, non_kapil_resend_otp_view, verify_kapil_student, kapil_reset_password_view, verify_non_kapil_student,
 non_kapil_reset_password_view, kapil_login)
from lmsapp.views import (manager_login, manager_dashboard,manager_logout,add_trainer,
    view_trainers,edit_trainer,delete_trainer,trainer_login,trainer_dashboard,trainer_logout,
    add_assessment,view_assessment,edit_assessment,delete_assessment,add_assessment_paper,
    view_assessment_paper, get_course_trainers, get_course_by_enrollment, submit_selected_trainers)



urlpatterns = [
    path('kapil-student/signup/', kapil_signup_view, name='kapil_signup'),
    path('non-kapil-student/signup/', non_kapil_signup_view, name='non_kapil_signup'),

    path('kapil-resend-otp/', kapil_resend_otp_view, name='kapil_resend_otp'),
    path('non-kapil-resend-otp/', non_kapil_resend_otp_view, name='non_kapil_resend_otp'),

    path('verify_kapil_student/', verify_kapil_student, name='verify_kapil_student'),
    path('verify_non_kapil_student/', verify_non_kapil_student, name='verify_non_kapil_student'),

    path('kapil_reset_password/', kapil_reset_password_view, name='kapil_reset_password'),
    path('non_kapil_reset_password/', non_kapil_reset_password_view, name='non_kapil_reset_password'),

    path('kapil_login/', kapil_login, name='kapil_login'),

    path('admin/', admin.site.urls),
    path('manager-login', manager_login, name='manager_login'),
    path('manager-dashboard', manager_dashboard, name='manager_dashboard'),
    path('add-trainer', add_trainer, name='add_trainer'),
    path('view-trainers', view_trainers, name='view_trainers'),
    path('edit-trainer/<int:trainer_id>', edit_trainer, name='edit_trainer'),
    path('delete-trainer/<int:trainer_id>',delete_trainer, name='delete_trainer'),
    path('manager-logout', manager_logout, name='manager_logout'),

    path('trainer-login', trainer_login, name='trainer_login'),
    path('trainer-dashboard', trainer_dashboard, name='trainer_dashboard'),
    path('add-assessment',add_assessment,name='add_assessment'),
    path('edit-assessment/<int:assessment_id>',edit_assessment, name='edit_assessment'),
    path('delete-assessment/<int:assessment_id>', delete_assessment, name='delete_assessment'),
    path('add-assessment-paper/<int:assessment_id>', add_assessment_paper, name='add_assessment_paper'),
    path('view-assessment-paper/<int:assessment_id>', view_assessment_paper, name='view_assessment_paper'),
    path('view-assessment',view_assessment,name='view_assessment'),
    path('trainer-logout', trainer_logout, name='trainer_logout'),
    
    path('get-course/', get_course_by_enrollment),
    path('get-course-trainers/', get_course_trainers, name='get_course_trainers'),
    path('submit_selected_trainers/', submit_selected_trainers, name='submit_selected_trainers'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

