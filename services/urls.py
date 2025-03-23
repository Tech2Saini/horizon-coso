from django.urls import path
from django.shortcuts import redirect
from .views import business_consultans

urlpatterns = [
    path("",lambda r: redirect('consultance'),name='services_home'),
    path("consultance/",business_consultans,name='consultance'),
    path("consultance/questions/",business_consultans,name='consultance'),
]
