import json
import os
import profile
from warnings import warn
from django.shortcuts import get_object_or_404, render
from django.db.models import Q

import random
import string

from resume_ai_app.decorators import candidate_required, recruiter_or_superuser_required, recruiter_required, superuser_required
from resume_ai_app.models import Application, CandidateProfile, Job, RecruiterProfile
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
# Create your views here.

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from .forms import ApplicationForm, ApplicationStatusForm, CandidateProfileForm, JobForm, ProfileUpdateForm, RecruiterForm, ResumeUploadForm, UserCreationForm, UserForm
from django.contrib.auth.decorators import permission_required
import sweetify

from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.conf import settings
from django.template.loader import render_to_string
from django.http import JsonResponse

from django.contrib.auth.models import User
from django.db.models import Count
from django.utils import timezone
from django.shortcuts import render
from datetime import timedelta
from django.db.models.functions import TruncDate

from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

from django.core.exceptions import PermissionDenied

import requests
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags



BASE_FLASK_API=settings.BASE_FLASK_API


'''-----------------page d'acceuil------------------- '''

def home(request):
    ctx = {}
    url_parameter = request.GET.get("q")

    if url_parameter:
        jobs = Job.objects.filter(title__icontains=url_parameter,isActive=True,is_open=True)
    else:
        jobs = Job.objects.filter(isActive=True, is_open=True)

    ctx["jobs"] = jobs
    does_req_accept_json = request.accepts("application/json")
    is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest" and does_req_accept_json

    if is_ajax_request:

        html = render_to_string(
            template_name="jobs_list.html", context={"jobs": jobs}
        )
        data_dict = {"html_from_view": html}
      
        return JsonResponse(data=data_dict, safe=False)

    return render(request, "index.html", context=ctx)


'''-----------------login /register /update profile -------------------'''

#@permission_required('add_recruiterprofile', raise_exception=True)
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Group.objects.get_or_create(name='Candidates')
            group=Group.objects.get(name='Candidates')
            user.groups.add(group)
            CandidateProfile.objects.create(user=user, email=form.cleaned_data['email'])

            send_candidate_welcome_email(request, user.id)

            #login(request, user)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def send_candidate_welcome_email(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    
    login_url = request.build_absolute_uri(reverse('login'))
    recipient_list = [user.email]
   
    subject = "Bienvenue dans AI Intelligent Recruitment Platform"
     
    html_content=render_to_string("profile/email_welcome_candidate_template.html",{'user':user,'login_url':login_url})
    text_content=strip_tags(html_content)

    email=EmailMultiAlternatives(
        subject,
        text_content,
        settings.EMAIL_HOST_USER, 
        recipient_list, 
    )
    email.attach_alternative(html_content,"text/html")
    email.send()
 
    
    sweetify.success(request, "<small>Félicitations ! Vous avez créé un compte chez AI Intelligent Recruitment Platform. Veuillez vérifier votre boîte de réception pour confirmer votre inscription.</small>")
    

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
def update_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user, user=request.user)
        if form.is_valid():
            form.save()
            sweetify.success(request, 'Votre profil a été mis à jour avec succès.')
            return redirect('dashboard')  # Rediriger après la mise à jour du profil
        else:
            sweetify.error(request, 'Une erreur est survenue. Veuillez vérifier le formulaire.')
    else:
        form = ProfileUpdateForm(instance=request.user, user=request.user)

    return render(request, 'profile/update_profile.html', {'form': form})

@login_required
def view_profile(request, user_id):
    # Récupérer l'utilisateur cible à partir de son ID
    user = get_object_or_404(User, id=user_id)
    
    profile = None
    jobs = None
    applications = None
    
    if hasattr(user, 'candidate_profile'):
        profile = user.candidate_profile
        applications = Application.objects.filter(candidate=profile,isActive=True)
    
    elif hasattr(user, 'recruiter_profile'):
        profile = user.recruiter_profile
        jobs = Job.objects.filter(recruiter=profile)

    return render(request, 'profile/view_profile.html', {'user': user, 'profile': profile, 'applications': applications, 'jobs': jobs})


'''-------------------candididate dashboard ----------------'''

@candidate_required
def candidate_dashboard(request):
    profile = request.user.candidate_profile
    applications = Application.objects.filter(candidate=profile, isActive=True)
       
       
    if profile.skills:    
       skills = profile.skills.split(',')   
    else:
        skills = ''

    if profile.education:    
       education = profile.education.split(',')   
    else:
        education = ''



    return render(request, 'cand/candidate_dashboard.html', {'profile': profile,'applications': applications,'skills': skills,'education':education})


@candidate_required
def edit_candidate_profile(request):
    profile = get_object_or_404(CandidateProfile, user=request.user)
    
    if request.method == 'POST':
        form = CandidateProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            sweetify.success(request, 'Profil mis à jour avec succès.')
            return redirect('candidate_dashboard')
    else:
        form = CandidateProfileForm(instance=profile)
    
    return render(request, 'cand/edit_candidate_profile.html', {'form': form})


@login_required
def serve_pdf(request, path):
    
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    
    if path!=None and os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="{}"'.format(os.path.basename(file_path))
        return response
    else:
        raise Http404("Le fichier n'existe pas")
  


def apply_for_job(request, id):
    
    
    if not request.user.is_authenticated:
        
        login_url = reverse('login')  # Remplacez 'login' par le nom de votre URL de connexion
        message = (
            '<small>Vous n\'êtes pas connecté.<br>'+
            'Veuillez vous connecter pour postuler.<a href="' + login_url + '"> Se Connecter</a></small>'
        )
        # Afficher un message d'avertissement si l'utilisateur n'est pas connecté
        sweetify.warning(request, message, persistent='OK')
        return redirect('home') 
    
    job = get_object_or_404(Job, id=id)
    candidate_profile = request.user.candidate_profile

    if Application.objects.filter(candidate=candidate_profile, job=job, isActive=True ).exists():
        sweetify.warning(request, 'Vous avez déjà postulé pour ce poste.', persistent='OK')
        return redirect('candidate_dashboard')

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            
            if not job.isActive or not job.is_open:
                sweetify.error(request, "<small>Desolé ,Le poste n'est pas disponible actuellement.</small>", persistent='OK')
                return redirect('home')
            
            application = form.save(commit=False)
            application.candidate = candidate_profile
            application.job = job
            application.status = 'in progress'
            application.save()
            sweetify.success(request, 'Votre candidature a été soumise avec succès.')
        
            return redirect('candidate_dashboard')  # Redirigez vers le tableau de bord du candidat après la candidature
    else:
        form = ApplicationForm()

    return render(request, 'cand/apply_for_job.html', {'job': job, 'form': form})


@candidate_required
def upload_resume(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES, instance=request.user.candidate_profile)
        if form.is_valid():
            form.save()
            # Extraire les informations du CV
            profile = request.user.candidate_profile
            resume_path = profile.resume_path.path

            base_url = BASE_FLASK_API
            with open(resume_path, 'rb') as pdf_file:
             
                files = {'pdf_file': pdf_file}
                response = requests.post(base_url+'/parse', files=files)
            
                if response.status_code == 200:
                    response.encoding = 'utf-8'
                    result = response.json()                  
                    candidate = get_object_or_404(CandidateProfile, pk=profile.id)

                    candidate.name=result["Name"]
    
                    candidate.email = result["Email"]
                    candidate.phone = result["Phone"]
                    candidate.education = ', '.join( result["Education"])
                       
                    #skills_list = [skill.strip() for skill in result["Skills"] if skill.strip()]
                    candidate.skills = ', '.join(result["Skills"])  # Convertir la liste en chaîne formatée

                    candidate.category=result["category"]
                   
                    candidate.save()

            return redirect('candidate_dashboard')
    else:
        form = ResumeUploadForm(instance=request.user.candidate_profile)
    return render(request, 'cand/upload_resume.html', {'form': form})


@candidate_required
def edit_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)

    if request.user.candidate_profile != application.candidate:
        sweetify.error(request, 'Vous ne pouvez modifier que vos propres candidatures.', persistent=':(')
        return redirect('candidate_dashboard')

    if request.method == 'POST':
        form = ApplicationForm(request.POST, instance=application)
        if form.is_valid():
            
            if not application.job.isActive or not application.job.is_open:
                sweetify.error(request, "<small>Desolé ,Le poste n'est pas disponible actuellement.</small>", persistent='OK')
                return redirect('candidate_dashboard')
            
            form.save()
            sweetify.success(request, 'Votre candidature a été mise à jour avec succès.')
            return redirect('candidate_dashboard')
    else:
        form = ApplicationForm(instance=application)

    return render(request, 'cand/apply_for_job.html', {'form': form, 'job': application.job})


@candidate_required
def delete_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)

    if request.user.candidate_profile != application.candidate:
        sweetify.error(request, 'Vous ne pouvez supprimer que vos propres candidatures.', persistent=':(')
        return redirect('candidate_dashboard')
    
    if not application.job.isActive or not application.job.is_open:
                sweetify.error(request, "<small>Desolé ,Le poste n'est pas disponible actuellement.</small>", persistent='OK')
                return redirect('candidate_dashboard')

    application.isActive = False
    application.save()
    sweetify.success(request, 'Votre candidature a été supprimée.')
    return redirect('candidate_dashboard')

''' ------------------------recruiter dashboard---------------'''




@recruiter_or_superuser_required
def recruiter_dashboard(request):
    
    profile = request.user if request.user.is_superuser else request.user.recruiter_profile

    # Récupérer tous les recruteurs si l'utilisateur est un superutilisateur
    recruiters = RecruiterProfile.objects.all() 

    # Filtrer les emplois actifs
    jobs = Job.objects.filter(isActive=True)

    # Récupérer les valeurs des filtres
    selected_recruiter = request.GET.get('recruiter', None)
    is_open_filter = request.GET.get('is_open', None)
   

    # Déboguer les valeurs des filtres
    print(f'Selected Recruiter: {selected_recruiter}')
   
    # Appliquer le filtre par recruteur
    if selected_recruiter:
        jobs = jobs.filter(recruiter__id=selected_recruiter)

   # Appliquer le filtre par statut
    if is_open_filter == 'open':
        jobs = jobs.filter(is_open=True)
    elif is_open_filter == 'closed':
        jobs = jobs.filter(is_open=False)

    return render(request, 'rec/list_jobs.html', {
        'profile': profile,
        'jobs': jobs,
        'recruiters': recruiters,
        'selected_recruiter': selected_recruiter,
       
    })

@recruiter_required
def post_job(request):
    profile = request.user.recruiter_profile
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = profile
            job.save()
            sweetify.success(request, 'Emploi posté avec succès.')
            return redirect('list_jobs')
    else:
        form = JobForm()
    return render(request, 'rec/post_job.html', {'form': form})

@recruiter_required
def edit_job(request, id):
    job = get_object_or_404(Job, id=id)    
    
    if request.user.recruiter_profile != job.recruiter:
        
        raise PermissionDenied("Vous n'avez pas l'autorisation de modifier cet emploi.")
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            sweetify.success(request, 'Emploi modifié avec succès.')
            return redirect('list_jobs')
    else:
        form = JobForm(instance=job)
    return render(request, 'rec/post_job.html', {'form': form})

@recruiter_required
def delete_job(request, id):
    job = get_object_or_404(Job, id=id, recruiter=request.user.recruiter_profile)
    if request.user.recruiter_profile != job.recruiter:
        raise PermissionDenied("Vous n'avez pas l'autorisation de modifier cet emploi.")
    
    job.isActive = False
    job.save()
    sweetify.success(request, 'Emploi supprimé avec succès.')
    return redirect('list_jobs')


@recruiter_or_superuser_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
      # Suppose que 'applications' est le champ ManyToMany ou ForeignKey pour les candidats
    return render(request, 'rec/detail_job.html', {'job': job})


@recruiter_or_superuser_required
def get_candidates_for_job(request, job_id):

    job = get_object_or_404(Job, id=job_id)
    applications = Application.objects.filter(job_id=job_id,isActive=True)
    nb=applications.count()

    criteria = job.requirements
    response_list = []
    applications_with_scores = []
    for item in applications:
        applications_with_scores.append({
            'application': get_object_or_404(Application, id=item.id),
            'score': 0
        }) 
    if(nb!=0 and criteria!=None):

        candidate_data = []
        for application in applications:
                candidate_data.append({
                    
                    'id_application': application.id,
                    
                    'skills': application.candidate.skills,                    
                })
      
        base_url = BASE_FLASK_API
        payload = {
                'criteria': criteria,     
                'candidates': candidate_data
            }
            
        response = requests.post(base_url + '/matching', json=payload)
            
        if response.status_code == 200:
                response_list = response.json()
                print(response_list)
                
                applications_with_scores = []
            
                for item in response_list:
                    
                    applications_with_scores.append({
                        'application': get_object_or_404(Application, id=item['id_application']),
                        'Similarity': item['Similarity']
                    })

    return render(request, 'rec/candidates_list.html', {'applications': applications_with_scores, 'job':job, 'nb_candidature':nb})


@recruiter_required
def dashboard_view(request):

    profile = request.user.recruiter_profile


    categories_data = CandidateProfile.objects.values('category').annotate(count=Count('category'))

    # Extraire les catégories et les comptes pour le graphique
    category_labels = json.dumps([entry['category'] for entry in categories_data if entry['category']])
    category_counts = json.dumps([entry['count'] for entry in categories_data if entry['category']])

    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    
    # Collecte du nombre de candidatures par jour
    daily_applications = (
        Application.objects
        .filter(created_at__gte=last_week)
        .annotate(day=TruncDate('created_at'))  # Assurez-vous d'avoir une date tronquée
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    
    # Créez une liste des 7 derniers jours
    days = [today - timedelta(days=i) for i in range(7, -1, -1)]
    daily_data = {str(day): 0 for day in days}

    # Mise à jour du dictionnaire avec les données réelles
    for entry in daily_applications:
        daily_data[str(entry['day'])] = entry['count']


    latest_jobs = Job.objects.filter(isActive=True).order_by('-created_at')[:3]

    # Récupérer les 5 dernières candidatures
    latest_applications = Application.objects.order_by('-created_at')[:3]  


    in_progress = Application.objects.filter(status='in progress').count()
    refused = Application.objects.filter(status='rejected').count()
    accepted = Application.objects.filter(status='accepted').count()


    context = {
        'new_applicants': Application.objects.filter(created_at__gte=timezone.now()-timedelta(days=7)).count(),
        'total_jobs':  Job.objects.filter(isActive=True).count(),
        'total_jobs_recruiter': Job.objects.filter(recruiter=profile,isActive=True).count() ,
        'active_jobs': Job.objects.filter(isActive=True,is_open=True).count(),
        'interview_scheduled': Application.objects.filter(status='in progress').count(),
        'total_candidates': CandidateProfile.objects.filter(isActive=True).count(),
        'new_candidates_7days': CandidateProfile.objects.filter(created_at__gte=timezone.now()-timedelta(days=7)).count(),
        'category_labels': category_labels,  
        'category_counts': category_counts,  
        'daily_labels': list(daily_data.keys()),
        'daily_values': list(daily_data.values()),
        'latest_jobs': latest_jobs,  
        'latest_applications': latest_applications,  
        'in_progress': in_progress,
        'refused': refused,
        'accepted': accepted,
    
    }




    return render(request, 'rec/dashboard.html', context)


@recruiter_or_superuser_required
def view_application(request, id):
    application = get_object_or_404(Application, id=id)
    return render(request, 'rec/view_application.html', {'application': application})

@recruiter_required
def edit_application_status(request, id):
    application = get_object_or_404(Application, id=id)
    job = application.job
    
    # Vérifiez que le recruteur connecté est celui qui a posté le job associé à la candidature
    if request.user.recruiter_profile != job.recruiter:

        #sweetify.error(request, "Vous n'avez pas l'autorisation de modifier le statut de cette candidature!")

        raise PermissionDenied("Vous n'avez pas l'autorisation de modifier le statut de cette candidature.")
        
    
    if request.method == 'POST':
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            sweetify.success(request, 'Statut de la candidature mis à jour avec succès.')
            return redirect('list_jobs')
    else:
        form = ApplicationStatusForm(instance=application)
    return render(request, 'rec/edit_application_status.html', {'form': form, 'application': application})

@recruiter_or_superuser_required
def recommend_candidates(request):
    if request.method == 'POST':
        criteria = request.POST.get('criteria')
        
        
        # Filter active candidates
        active_candidates = CandidateProfile.objects.filter(isActive=True)
        
        # Prepare the data to send to the Flask API
        candidate_data = []
        for candidate in active_candidates:
            candidate_data.append({
                'id': candidate.id,
                'name': candidate.name,
                'skills': candidate.skills,
                'email': candidate.email,
            })
        print(candidate_data)
        base_url = BASE_FLASK_API
        payload = {
            'criteria': criteria,
            
            'candidates': candidate_data
        }
        
        response = requests.post(base_url + '/recommend', json=payload)
        
        if response.status_code == 200:
            recommendations = response.json()
        else:
            recommendations = []

        return render(request, 'rec/recommend_candidates.html', {'candidates': recommendations, 'criteria': criteria})
    
    return render(request, 'rec/recommend_candidates.html')


@recruiter_or_superuser_required
def candidate_details(request, candidate_id):
    candidate = get_object_or_404(CandidateProfile, id=candidate_id, isActive=True)
    applications = Application.objects.filter(candidate=candidate, isActive=True)
    return render(request, 'rec/candidate_details.html', {
        'candidate': candidate,
        'applications': applications
    })

@recruiter_or_superuser_required
def candidate_applications(request, candidate_id):
    candidate = get_object_or_404(CandidateProfile, id=candidate_id, isActive=True)
    applications = Application.objects.filter(candidate=candidate, isActive=True)
    html = render_to_string('rec/candidate_applications.html', {'applications': applications})
    return HttpResponse(html)

''' ----------------admin dashboard--------------- '''

@superuser_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    categories_data = CandidateProfile.objects.values('category').annotate(count=Count('category'))

    # Extraire les catégories et les comptes pour le graphique
    category_labels = json.dumps([entry['category'] for entry in categories_data if entry['category']])
    category_counts = json.dumps([entry['count'] for entry in categories_data if entry['category']])

    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    
    # Collecte du nombre de candidatures par jour
    daily_applications = (
        Application.objects
        .filter(created_at__gte=last_week)
        .annotate(day=TruncDate('created_at'))  # Assurez-vous d'avoir une date tronquée
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    
    # Créez une liste des 7 derniers jours
    days = [today - timedelta(days=i) for i in range(7, -1, -1)]
    daily_data = {str(day): 0 for day in days}

    # Mise à jour du dictionnaire avec les données réelles
    for entry in daily_applications:
        daily_data[str(entry['day'])] = entry['count']


    latest_jobs = Job.objects.filter(isActive=True).order_by('-created_at')[:3]

    # Récupérer les 5 dernières candidatures
    latest_applications = Application.objects.order_by('-created_at')[:3]  


    in_progress = Application.objects.filter(status='in progress').count()
    refused = Application.objects.filter(status='rejected').count()
    accepted = Application.objects.filter(status='accepted').count()


    context = {
        'new_applicants': Application.objects.filter(created_at__gte=timezone.now()-timedelta(days=7)).count(),
        'total_jobs':  Job.objects.filter(isActive=True).count(),
        'total_recruiters': RecruiterProfile.objects.filter().count() ,
        'active_jobs': Job.objects.filter(isActive=True,is_open=True).count(),
        'interview_scheduled': Application.objects.filter(status='in progress').count(),
        'total_candidates': CandidateProfile.objects.filter(isActive=True).count(),
        'new_candidates_7days': CandidateProfile.objects.filter(created_at__gte=timezone.now()-timedelta(days=7)).count(),
        'category_labels': category_labels,  
        'category_counts': category_counts,  
        'daily_labels': list(daily_data.keys()),
        'daily_values': list(daily_data.values()),
        'latest_jobs': latest_jobs,  
        'latest_applications': latest_applications,  
        'in_progress': in_progress,
        'refused': refused,
        'accepted': accepted,
    
    }


    
    return render(request, 'admin/admin_dashboard.html', context)

@superuser_required
def manage_recruiters(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        recruiter_form = RecruiterForm(request.POST)

        if user_form.is_valid() and recruiter_form.is_valid():
            
            # Crée l'utilisateur avec le mot de passe généré
            user = user_form.save()
        
            Group.objects.get_or_create(name='Recruiters')
            group = Group.objects.get(name='Recruiters')
            user.groups.add(group)
            
            recruiter = recruiter_form.save(commit=False)
            recruiter.user = user
            recruiter.save()
            print(user.id)

     
  
            sweetify.success(request, 'Utilisateur ajouté avec succès.')
          
            return redirect(f'{reverse("manage_recruiters")}?user_id={user.id}')
           
    user_form = UserForm()
    recruiter_form = RecruiterForm()

    recruiters = RecruiterProfile.objects.all()
    return render(request, 'admin/manage_recruiters.html', {
        'recruiters': recruiters,
        'user_form': user_form,
        'recruiter_form': recruiter_form
    })


def generate_password(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

@login_required
def send_recruiter_welcome_email(request, user_id):
    user = get_object_or_404(User, id=user_id)
    plain_password = generate_password()
    user.set_password(plain_password) 
    user.save()
    
    login_url = request.build_absolute_uri(reverse('login'))
    recipient_list = [user.email]
   
    subject = "Email d'authentification - Intelligent Recruitment Platform"
     
    html_content=render_to_string("admin/email_auth_template.html",{'title':'test','user':user,'login_url':login_url,'password': plain_password})
    text_content=strip_tags(html_content)

    email=EmailMultiAlternatives(
        subject,
        text_content,
        settings.EMAIL_HOST_USER, 
        recipient_list, 
    )
    email.attach_alternative(html_content,"text/html")
    email.send()
 
    
    sweetify.success(request, "Email de bienvenue envoyé avec succès à l'utilisateur.")
    return redirect('manage_recruiters')


@superuser_required
def edit_recruiter(request, pk):
    recruiter = get_object_or_404(RecruiterProfile, pk=pk)
    user = recruiter.user

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        recruiter_form = RecruiterForm(request.POST, instance=recruiter)

        if user_form.is_valid() and recruiter_form.is_valid():
            user_form.save()
            recruiter_form.save()
            sweetify.success(request, 'Utilisateur modifié avec succès.')
            return redirect('manage_recruiters')
    else:
        user_form = UserForm(instance=user)
        recruiter_form = RecruiterForm(instance=recruiter)
     
    recruiters = RecruiterProfile.objects.filter(isActive=True)
    return render(request, 'admin/manage_recruiters.html', {
        'recruiters': recruiters,
        'user_form': user_form,
        'recruiter_form': recruiter_form,
        'edit': True,
        'recruiter_id': pk,
      
    })

@superuser_required
def delete_recruiter(request, pk):
    recruiter = get_object_or_404(RecruiterProfile, pk=pk)
    recruiter.isActive = False
    recruiter.user.is_active=False
    recruiter.save()
    sweetify.success(request, 'Utilisateur désactivé avec succès.')
    return redirect('manage_recruiters')

@superuser_required
def activate_recruiter(request, pk):
    recruiter = get_object_or_404(RecruiterProfile, pk=pk)
    recruiter.isActive = True
    recruiter.user.is_active=True
    recruiter.save()
    sweetify.success(request, 'Utilisateur réactivé avec succès.')
    return redirect('manage_recruiters')