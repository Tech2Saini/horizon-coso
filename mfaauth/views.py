import os,time
import cv2
import re
from pyzbar.pyzbar import decode
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from .models import MFASecret
from .forms import MFAUploadForm
from django.http import JsonResponse
import pyotp
from django import forms

# login user 
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout


# Function to extract secret from a QR code image
def extract_secret_from_qr(qr_image_path):
    image = cv2.imread(qr_image_path)  # Load image
    decoded_qr = decode(image)

    if decoded_qr:
        qr_data = decoded_qr[0].data.decode("utf-8")  # Extract QR text

        secret = re.search(r"secret=([A-Z0-9]+)", qr_data)  # Extract secret
        secret = secret.group(1) if  secret else None
        
        issuer_match = re.search(r"issuer=([^&]+)", qr_data)
        issuer = issuer_match.group(1) if issuer_match else None

        email_match = re.search(r"otpauth://totp/([^?]+)", qr_data)
        email = email_match.group(1).split(":") if email_match else None

        if email is not None:
            email = email[1] if len(email)>1  else email
        

        if secret:
            return {
                "secret":secret,
                "email":email,
                "issuer":issuer
            }
        else:
            raise ValueError("No secret key found in QR code.")
    else:
        raise ValueError("QR code could not be decoded.")

# Restrict view to superusers
def is_superuser(user):
    return user.is_superuser

# Admin-only view to upload/update MFA QR codes
# @login_required
# @user_passes_test(is_superuser)
def upload_mfa_qr(request):
    if request.user.is_anonymous or not request.user.is_superuser:
        return redirect("mfa_login")
    
    if request.method == "POST":
        form = MFAUploadForm(request.POST, request.FILES)
        if form.is_valid():
            qr_image = form.cleaned_data["qr_code_image"]

            try:
                temp_path = f"temp_{time.time()//1}.png"
                with open(temp_path, "wb") as f:
                    for chunk in qr_image.chunks():
                        f.write(chunk)
                
                data = extract_secret_from_qr(temp_path)

                if os.path.isfile(temp_path):
                    os.remove(temp_path)

                new_auth,created = MFASecret.objects.get_or_create(email=data['email'],issuer=data['issuer'])

                if created:
                    new_auth.secret = data['secret']
                    new_auth.qr_code_image = qr_image
                    new_auth.save()

                    messages.success(request,f"The MFA-Secret are added successfully as \nEmail:{data['email']}\nIssuer: {data['issuer']}")
                
                else:

                    if new_auth.secret!=data["secret"]:
                        new_auth.secret = data["secret"]                
                        new_auth.qr_code_image = qr_image                
                        new_auth.save()

                        messages.info(request,f"We Find the secrets with same email and issuer \n We update it \nEmail:{data['email']}\nIssuer: {data['issuer']}")

                    else:
                        messages.warning(request,f"The secrets already exists")
                        
            except ValueError as e:
                messages.error(request, f"Error: {str(e)}")
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")

    else:
        form = MFAUploadForm()

    return render(request, "upload_mfa_qr.html", {"form": form})


# @login_required
def showAndUpdateOtp(request):
    if request.user.is_anonymous:
        return redirect("mfa_login")  # Redirect to OTP page

    secrets_by_issuer = {}

    mfa_entries = MFASecret.objects.all()  # Fetch all stored OTP secrets
    
    for entry in mfa_entries:
        totp = pyotp.TOTP(entry.secret)
        otp = totp.now()  # Generate OTP
        
        if entry.issuer not in secrets_by_issuer:
            secrets_by_issuer[entry.issuer] = []
        
        secrets_by_issuer[entry.issuer].append({
            "email": entry.email,
            "otp": otp,
            "uuid": entry.key,  # Unique identifier for refresh
            "issuer": entry.issuer,  # Unique identifier for refresh
        })

    context = {
        "secrets_by_issuer":secrets_by_issuer,
        "issuers": secrets_by_issuer.keys(),  # List of issuers for tab navigation
    }

    return render(request, "showotp.html", context)

@login_required
def get_otp(request):
    """Returns a continuously updating OTP for the authenticated user."""

    if request.method == "POST":
        try:
            key = request.POST.get("key")

            mfa_secret = MFASecret.objects.get(key=key)

            totp = pyotp.TOTP(mfa_secret.secret)
            # otp = totp.now()
            otp = totp.at(time.time())  # ✅ Ensure correct timing

            return JsonResponse({"otp": otp})
        except MFASecret.DoesNotExist:
            return JsonResponse({"error": "MFA secret not found"}, status=404)
        


class LoginForm(forms.Form):
    email = forms.EmailField(
        max_length=150, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email address'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

def user_login(request):

    if request.user.is_authenticated:
        return redirect("show_otp")  # Redirect to OTP page
    
    form = LoginForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            email = form.cleaned_data["email"]  
            password = form.cleaned_data["password"]

            get_user = User.objects.filter(email = email.lower())
            username = get_user[0].username if get_user.count()>0 else "_ _"

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "Login successful! 🔓")
                return redirect("show_otp")  # Redirect to OTP page
            else:
                form.add_error(None, "Invalid email or password. Please try again. ❌")

    return render(request, "login.html", {"form": form})


def logOut_User(request):

    logout(request)

    request.session.flush()  # Clears session data

    return redirect('mfa_login')


def session_check(request):
    if request.user.is_authenticated:
        # Do NOT modify the session, just return status
        return JsonResponse({"is_authenticated": True}, status=200)
    else:
        return JsonResponse({"is_authenticated": False}, status=401)