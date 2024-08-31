from django.conf import settings
from django.contrib import admin
from django.urls import path,include
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.conf.urls import url
from django.conf.urls.static import static

from resume_ai_app import views
from resume_ai_app.forms import CustomAuthenticationForm


urlpatterns = [
    path('', views.home,name="home"),

    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', LoginView.as_view(template_name='login.html', authentication_form=CustomAuthenticationForm), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('reset_password/',PasswordResetView.as_view(template_name='reset_pass/password_reset.html',html_email_template_name='reset_pass/password_reset_email.html',subject_template_name="reset_pass/password_reset_subject.txt",),name='reset_password' ),
    
    path('reset_password_send',PasswordResetDoneView.as_view(template_name='reset_pass/password_reset_sent.html'),name='password_reset_done' ),
    path('reset/<uidb64>/<token>',PasswordResetConfirmView.as_view(template_name='reset_pass/password_reset_form.html'),name='password_reset_confirm' ),
    path('reset_password_complete/',PasswordResetCompleteView.as_view(template_name='reset_pass/password_reset_done.html'),name='password_reset_complete' ),
    
    path('profile/edit/', views.update_profile, name='update_profile'),
    path('profile/<int:user_id>/', views.view_profile, name='view_profile'),

    path('candidate_dashboard/', views.candidate_dashboard, name='candidate_dashboard'),
    path('media/<path:path>', views.serve_pdf, name='serve_pdf'),
    path('apply/<int:id>/', views.apply_for_job, name='apply_for_job'),
    path('upload_resume/', views.upload_resume, name='upload_resume'),
    path('edit_application/<int:application_id>/', views.edit_application, name='edit_application'),
    path('delete_application/<int:application_id>/', views.delete_application, name='delete_application'),
    path('edit-profile/', views.edit_candidate_profile, name='edit_candidate_profile'),
        



    path('recruiter/jobs/', views.recruiter_dashboard, name='list_jobs'),
    path('recruiter/post-job/', views.post_job, name='post_job'),
    path('recruiter/edit-job/<int:id>/', views.edit_job, name='edit_job'),
    path('recruiter/delete-job/<int:id>/', views.delete_job, name='delete_job'),
    path('recruiter/view-application/<int:id>/', views.view_application, name='view_application'),
    path('recruiter/edit-application-status/<int:id>/', views.edit_application_status, name='edit_application_status'),
    path('recruiter/recommend-candidates/', views.recommend_candidates, name='recommend_candidates'), 
    path('recruiter/candidate_applications/<int:candidate_id>/', views.candidate_applications, name='candidate_applications'),
    
    path('job/<int:job_id>/candidates/', views.get_candidates_for_job, name='job_candidates'),
    path('recruiter/dashboard/', views.dashboard_view, name='recruiter_dashboard'),
     path('job/<int:job_id>/', views.job_detail, name='job_detail'),


    
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage_recruiters/', views.manage_recruiters, name='manage_recruiters'),
    path('edit_recruiter/<int:pk>/', views.edit_recruiter, name='edit_recruiter'),
    path('delete_recruiter/<int:pk>/', views.delete_recruiter, name='delete_recruiter'),
    path('activate_recruiter/<int:pk>/', views.activate_recruiter, name='activate_recruiter'),

    path('send-email/<int:user_id>/', views.send_recruiter_welcome_email, name='send_recruiter_welcome_email'),

    
 

    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)