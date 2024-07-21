import os
from django.shortcuts import get_object_or_404, render

from resume_ai_app.models import Application, CandidateProfile, Job, RecruiterProfile
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
# Create your views here.

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from .forms import ApplicationForm, ResumeUploadForm, UserCreationForm
from django.contrib.auth.decorators import permission_required
import sweetify

def home(request):
    jobs_available = Job.objects.filter(is_open=True)
   
    return render(request,"index.html",{'jobs': jobs_available})

# resume_ai_app/views.py



# resume_ai_app/views.py


#@permission_required('add_recruiterprofile', raise_exception=True)
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data['role']
            if role == 'candidate':
                Group.objects.get_or_create(name='Candidates')
                group=Group.objects.get(name='Candidates')
                user.groups.add(group)
                CandidateProfile.objects.create(user=user)
            elif role == 'recruiter':
                Group.objects.get_or_create(name='Recruiters')
                group = Group.objects.get(name='Recruiters')
                user.groups.add(group)
                RecruiterProfile.objects.create(user=user)
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def dashboard(request):
    if request.user.is_superuser:
        # Redirect to admin dashboard or any other admin-specific view
        return redirect('admin_dashboard')
    
    elif request.user.groups.filter(name='Candidates').exists():
        return redirect('candidate_dashboard')
    elif request.user.groups.filter(name='Recruiters').exists():
        return redirect('recruiter_dashboard')

@login_required
def candidate_dashboard(request):
    profile = request.user.candidate_profile
    applications = Application.objects.filter(candidate=profile)
    skills = profile.skills.split(',')
    return render(request, 'candidate_dashboard.html', {'profile': profile,'applications': applications,'skills': skills,})

@login_required
def recruiter_dashboard(request):
    profile = request.user.recruiter_profile
    return render(request, 'recruiter_dashboard.html', {'profile': profile})

@login_required
def admin_dashboard(request):
    profile = request.user
    return render(request, 'admin_dashboard.html', {'profile': profile})


from django.http import FileResponse, Http404
from django.conf import settings



    
def serve_pdf(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    print(file_path)
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="{}"'.format(os.path.basename(file_path))
        return response
    else:
        raise Http404("Le fichier n'existe pas")


    

@login_required
def apply_for_job(request, id):
    print(id)
    
    job = get_object_or_404(Job, id=id)
    print(job)
    candidate_profile = request.user.candidate_profile

    if Application.objects.filter(candidate=candidate_profile, job=job).exists():
        sweetify.warning(request, 'Vous avez déjà postulé pour ce poste.', persistent='OK')
        return redirect('candidate_dashboard')

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.candidate = candidate_profile
            application.job = job
            application.status = 'in progress'
            application.save()
            sweetify.success(request, 'Votre candidature a été soumise avec succès.')
        
            return redirect('candidate_dashboard')  # Redirigez vers le tableau de bord du candidat après la candidature
    else:
        form = ApplicationForm()

    return render(request, 'apply_for_job.html', {'job': job, 'form': form})


@login_required
def upload_resume(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES, instance=request.user.candidate_profile)
        if form.is_valid():
            form.save()
            return redirect('candidate_dashboard')
    else:
        form = ResumeUploadForm(instance=request.user.candidate_profile)
    return render(request, 'upload_resume.html', {'form': form})

