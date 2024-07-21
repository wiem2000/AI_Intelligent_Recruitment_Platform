# resume_ai_app/signals.py

from django.contrib.auth.models import Group, User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CandidateProfile, RecruiterProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create Candidate and Recruiter Groups
        Group.objects.get_or_create(name='Candidates')
        Group.objects.get_or_create(name='Recruiters')
        
        # Create Candidate Profile
        if instance.groups.filter(name='Candidates').exists():
            CandidateProfile.objects.create(user=instance)
        elif instance.groups.filter(name='Recruiters').exists():
            RecruiterProfile.objects.create(user=instance)
