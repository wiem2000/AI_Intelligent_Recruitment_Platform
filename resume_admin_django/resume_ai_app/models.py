from django.db import models
from django.contrib.auth.models import User


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)

    class Meta:
        abstract = True


    
class CandidateProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    resume_path = models.FileField(upload_to='resumes',blank=True, null=True)
    name = models.CharField(max_length=255,blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20,blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100,blank=True, null=True)

    def __str__(self):
        return self.user.username
    
class RecruiterProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recruiter_profile')
    company_name = models.CharField(max_length=255)
    company_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username


class Job(BaseModel):
    recruiter = models.ForeignKey(RecruiterProfile, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    job_type = models.CharField(max_length=50, choices=(('internship', 'Stage'), ('job', 'Emploi')))
    location = models.CharField(max_length=255,blank=True, null=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    is_open = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
class Application(BaseModel):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=50, choices=(('in progress', 'En cours'), ('accepted', 'Acceptée'), ('rejected', 'Refusée')))
    applied_at = models.DateTimeField(auto_now_add=True)
    recruiter_comment = models.TextField(blank=True, null=True)
    cover_letter = models.TextField(blank=True, null=True)


    def __str__(self):
        return f"{self.candidate.user.username} - {self.job.title}"
