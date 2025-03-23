from django.shortcuts import render
from home.models import FAQ
# Create your views here.

def business_consultans(request):
    faqs = FAQ.objects.filter(is_active = True,service__name = "Business Consulting")
    return render(request,'business_consulting.html',{'faqs':faqs})