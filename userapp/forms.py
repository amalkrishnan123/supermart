from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.forms import PasswordResetForm

class UserForm(UserCreationForm):
    mobile=forms.CharField(max_length=10,required=True)
    email=forms.EmailField()
    class Meta:
        model = User
        fields = ["username","email","mobile","password1","password2"]

        # for unique email
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email
#it is used to remove inbuilt warnings to user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove all default Django help texts
        for field_name in self.fields:
            self.fields[field_name].help_text = ""
        # Add Bootstrap classes + placeholders
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter Username',
            'autocomplete': 'off'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter Email'
        })
        self.fields['mobile'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter Mobile',
            'autocomplete': 'off'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })

# class CustomPasswordResetForm(PasswordResetForm):
#     def clean_email(self):
#         email = self.cleaned_data['email']
#         if not User.objects.filter(email=email).exists():
#             raise forms.ValidationError("This email is not registered with us.")
#         return email
    
#     def get_email_context(self, user):
#         context = super().get_email_context(user)
#         context["domain"] = "127.0.0.1:8000"   # your local domain
#         context["protocol"] = "http"          # or https if using SSL
#         return context


