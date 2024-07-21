# resume_ai_app/forms.py

from django import forms
from django.contrib.auth.models import User

from resume_ai_app.models import Application, CandidateProfile

class UserCreationForm(forms.ModelForm):
    
    role = forms.ChoiceField(choices=(('candidate', 'Candidate'), ('recruiter', 'Recruiter')))
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirm password')

    class Meta:
        model = User
        fields = ['username', 'password','confirm_password', 'role']
        error_messages = {
            'username': {
                'required': 'Ce champ est requis.',
                'max_length': 'Le nom d\'utilisateur doit contenir 150 caractères ou moins.',
                'invalid': 'Lettres, chiffres et @/./+/-/_ uniquement.',
            },
            'password': {
                'required': 'Ce champ est requis.',
            },
              'confirm_password': {
                'required': 'Ce champ est requis.',
                'invalid': 'Les mots de passe ne correspondent pas.',
            },
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Les mots de passe ne correspondent pas.")

        return cleaned_data



    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class':'form-control'})
        self.fields['role'].widget.attrs.update({'class':'form-control'})
        self.fields['confirm_password'].widget.attrs.update({'class':'form-control'})



class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }


class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = CandidateProfile
        fields = ['resume_path']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['resume_path'].widget.attrs.update({'class': 'form-control'})
     