# resume_ai_app/forms.py

from django import forms
from django.contrib.auth.models import User

from resume_ai_app.models import Application, CandidateProfile, Job, RecruiterProfile

from django.contrib.auth.forms import AuthenticationForm


class CustomAuthenticationForm(AuthenticationForm):
    def clean(self):
        try:
            return super().clean()
        except forms.ValidationError:
            # Remplacer le message d'erreur par défaut
            raise forms.ValidationError(
                "Nom d'utilisateur ou mot de passe incorrect. Veuillez réessayer.",
                code='invalid_login',
            )
        

                               

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
               
            },
            'password': {
                'required': 'Ce champ est requis.',
            },
              'confirm_password': {
                'required': 'Ce champ est requis.',
                'invalid': 'Les mots de passe ne correspondent pas.',
            },
        }
        help_texts = {
            'username': '',  # Remove help text
           
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


class UserForm(forms.ModelForm):



    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control','required': True}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'username': '',  # Supprimer le texte d'aide
            'email': '',  # Supprimer le texte d'aide
            'first_name': '',  # Supprimer le texte d'aide
            'last_name': ''  # Supprimer le texte d'aide
        }

      
        

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
            hashed_password = self.instance.password
            self.fields['password'] = forms.CharField(
                label='Mot de passe',
                widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
                initial=self.mask_password(hashed_password),
                required=False,  # Indiquer que ce champ n'est pas requis pour la validation
                help_text=f"<small style='color: red;font-size:small'><b>Algorithme:</b> {self.get_password_hash_algorithm(hashed_password)}. Les mots de passe ne sont pas enregistrés en clair, ce qui ne permet pas d’afficher le mot de passe de cet utilisateur, mais il est possible de le changer en utilisant ce formulaire</small>"
            )

    def mask_password(self, password):
        return password[:3] + '*' * (len(password) - 3)
    

    def get_password_hash_algorithm(self, password):
        try:
            return identify_hasher(password).algorithm
        except ValueError:
            return 'Inconnu'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if not self.instance.pk:  # Si c'est un nouvel utilisateur
            user.set_password('0000')  # Définir le mot de passe par défaut
        if commit:
            user.save()
        return user
            
class RecruiterForm(forms.ModelForm):
    class Meta:
        model = RecruiterProfile
        fields = ['company_name', 'company_description']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_description': forms.Textarea(attrs={'class': 'form-control','rows':5}),
        }


class CandidateProfileForm(forms.ModelForm):
    class Meta:
        model = CandidateProfile
        fields = ['name', 'email', 'phone', 'education', 'skills', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'education': forms.Textarea(attrs={'class': 'form-control','rows':4}),
            'skills': forms.Textarea(attrs={'class': 'form-control','rows':5}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
        }


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


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'requirements', 'job_type', 'location']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'requirements': forms.Textarea(attrs={'class': 'form-control'}),
            'job_type': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super(JobForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control mt-1'})

class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status', 'recruiter_comment']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'recruiter_comment': forms.Textarea(attrs={'class': 'form-control'}),
        }


class ProfileUpdateForm(forms.ModelForm):
    old_password = forms.CharField(widget=forms.PasswordInput, required=False, label="Ancien mot de passe")
    new_password = forms.CharField(widget=forms.PasswordInput, required=False, label="Nouveau mot de passe")
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False, label="Confirmer le nouveau mot de passe")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'username': '',  # Remove help text
         }
        

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # On passe l'utilisateur actuel pour la validation
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class':'form-control'})
        self.fields['new_password'].widget.attrs.update({'class':'form-control'})
        self.fields['confirm_password'].widget.attrs.update({'class':'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        # Validation de l'ancien mot de passe si l'utilisateur souhaite le changer
        if old_password or new_password or confirm_password:
            if not self.user.check_password(old_password):
                self.add_error('old_password', "L'ancien mot de passe est incorrect.")
            if new_password != confirm_password:
                self.add_error('confirm_password', "Les nouveaux mots de passe ne correspondent pas.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password')

        if new_password:
            user.set_password(new_password)
        
        if commit:
            user.save()

        return user