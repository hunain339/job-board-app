from django import forms
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class BaseRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email  # Ensure username is unique and set to email
        if commit:
            user.save()
        return user

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password != password_confirm:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

class CandidateRegisterForm(BaseRegisterForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'candidate'
        user.is_active = True  # Active immediately; add email verification later
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            UserProfile.objects.get_or_create(user=user)
        return user

class EmployerRegisterForm(BaseRegisterForm):
    company_name = forms.CharField(max_length=255)
    company_description = forms.CharField(widget=forms.Textarea, required=False)

    class Meta(BaseRegisterForm.Meta):
        fields = BaseRegisterForm.Meta.fields + ['company_name', 'company_description']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'employer'
        user.is_active = True  # Active immediately; add email verification later
        user.is_approved_employer = True  # Auto-approve for now
        user.company_name = self.cleaned_data["company_name"]
        user.company_description = self.cleaned_data["company_description"]
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            UserProfile.objects.get_or_create(user=user)
        return user
