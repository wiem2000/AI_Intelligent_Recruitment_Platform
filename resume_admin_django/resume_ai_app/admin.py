from django.contrib import admin



# Register your models here.
# admin.site.register(User)


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import CandidateProfile, RecruiterProfile, Job, Application


# Inline Model Admins
class CandidateProfileInline(admin.StackedInline):
    model = CandidateProfile
    can_delete = False
    verbose_name_plural = 'Candidate Profile'

class RecruiterProfileInline(admin.StackedInline):
    model = RecruiterProfile
    can_delete = False
    verbose_name_plural = 'Recruiter Profile'


# Custom User Admin
class UserAdmin(BaseUserAdmin):
    inlines = [CandidateProfileInline, RecruiterProfileInline]


# Register models
#admin.site.unregister(User)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Job)
admin.site.register(Application)
