from django.conf import settings
from django.contrib import admin
from django.urls import path,include
from django.contrib.auth.views import LoginView, LogoutView
from django.conf.urls import url
from django.conf.urls.static import static

from resume_ai_app import views

urlpatterns = [
    path('', views.home,name="home"),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('candidate_dashboard/', views.candidate_dashboard, name='candidate_dashboard'),
    path('recruiter_dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('media/<path:path>', views.serve_pdf, name='serve_pdf'),
    
    path('apply/<int:id>/', views.apply_for_job, name='apply_for_job'),

    path('upload_resume/', views.upload_resume, name='upload_resume'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)