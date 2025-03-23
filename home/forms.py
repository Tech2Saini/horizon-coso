from django import forms
from .models import Contact,FAQ
import re

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['fullname', 'email', 'phone_number', 'subject', 'message']
        widgets = {
            'fullname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Phone (Optional)'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control h-100', 'placeholder': 'Your Message'}),
        }

    def clean_fullname(self):
        fullname = self.cleaned_data.get('fullname')
        if len(fullname) < 3:
            raise forms.ValidationError("Full name must be at least 3 characters long.")
        return fullname

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise forms.ValidationError("Enter a valid email address.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone and not re.match(r'^\+?1?\d{9,15}$', phone):  # Basic phone validation
            raise forms.ValidationError("Enter a valid phone number (9-15 digits).")
        return phone

    def clean_message(self):
        message = self.cleaned_data.get('message')
        if len(message) < 50:
            raise forms.ValidationError("Message must be at least 50 characters long.")
        return message

class FaqForms(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['service', 'question','email']
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control','id':'questionInput'}),
            'question': forms.TextInput(attrs={'class': 'form-control','placeholder':'write your question here...'}),
            'email': forms.EmailInput(attrs={'class': 'form-control','placeholder':'Email address'}),
        }

class FaqAnswerForms(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['question','answer']
        widgets = {
            'question': forms.TextInput(attrs={'class': 'form-control'}),
            'answer': forms.TextInput(attrs={'class': 'form-control','id':'questionInput','readonly':True}),
        }