
from django.urls import path,include
from home.views import home
from django.views.generic import RedirectView
from django.urls import re_path

from .views import contact_view,askQuestions,answerQuestions,questionAction,userAnswer,privacyPolicy,termsConditions


urlpatterns = [
    path('',home,name='home'),
    re_path(r'^favicon\.ico$', RedirectView.as_view(url='/static/img/favicon.ico', permanent=True)),
    path('contact/', contact_view, name='contact'),
    path("ckeditor/", include('ckeditor_uploader.urls')), # <-- here
    path("privacy-policy/",privacyPolicy, name="privacy_policy"),
    path("terms-conditions/",termsConditions, name="terms_condition"),
    path('ask-questions/',askQuestions,name='questions'),
    path('answer-questions/your-answer/<int:id>/',userAnswer,name='user_answer'),
    path('answer-questions/',answerQuestions,name='answers'),
    path('answer-questions/<int:n>/<str:action>/',questionAction,name='answer_action'),
]
