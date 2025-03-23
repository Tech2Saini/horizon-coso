from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .forms import ContactForm
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlencode
from datetime import datetime
from django.core.mail import EmailMessage
from email.utils import formataddr
from django.contrib.auth.decorators import login_required, user_passes_test
import json
from datetime import datetime


from .models import TeamMember,PricingPlan,FAQ
from .forms import FaqForms,FaqAnswerForms


################################### Quick Funtions #########################
# Restrict view to superusers
def is_superuser(user):
    return user.is_superuser

def home(request):
    teamMember  = TeamMember.objects.all().order_by('order')
    pricingPlan  = PricingPlan.objects.all()
    faqs  = FAQ.objects.filter(service=None,is_active=True)
    return render(request,'home.html',{'team':teamMember,'pricing':pricingPlan,'faqs':faqs})

def contact_view(request):


    if request.method == 'POST':
        form = ContactForm(request.POST)

        
        if form.is_valid():
            form.save()

            name = request.POST.get("fullname")
            email = request.POST.get("email")
            subject = request.POST.get("subject")
            message = request.POST.get("message")
            phone = request.POST.get("phone_number")

           
            try:
                # Send the email
                send_Email(name,email,subject,message,phone)
                messages.add_message(request, messages.SUCCESS, "Your message send successfully.")
                messages.add_message(request, messages.INFO, "Our team will connect you soon...")
                
                messages.add_message(request, messages.success, "Form is submited, Our team connect you soon!")

            except Exception as e:
                # return JsonResponse({"success": False, "message": str(e)})
                messages.add_message(request, messages.DEBUG, str(e))


            form = ContactForm()
        

    else:
        form = ContactForm()

    return render(request,'contact.html',{'form':form})

def privacyPolicy(request):
    return render(request,'privacypolicy.html')

def termsConditions(request):
    return render(request,'terms.html')

def send_Email(name,email,subject,message,phone):
    # Render the email template with dynamic data
    email_html_content = render_to_string("contact_email.html", {
        "name": name,
        "email": email,
        "phone":phone,
        "subject": subject,
        "message": message,
        "year":datetime.now().year
    })

    email_message = EmailMessage(
        subject=f"New Contact Request: {subject}",
        body=email_html_content,
        from_email=formataddr(("Horizon Co&So", settings.EMAIL_HOST_USER)),  
        to=[settings.ADMIN_EMAIL],
    )

    email_message.content_subtype = "html"
    email_message.send()

# Helper function to get user IP
def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

def askQuestions(request):

    post_message = False
    if request.method ==  "POST":
        form = FaqForms(request.POST)
        question = request.POST.get('question')
        service = request.POST.get('service',None)
        full_url = request.build_absolute_uri('/')[:-1]  # Removes trailing slash
        if form.is_valid():
            form = form.save()

            try:
                SendQuestionMail(question=question,service=service,answer_url=f"{full_url}/answer-questions/")
                post_message = True

                messages.success(request,"Question is submit",extra_tags='success')

            except Exception as e:
                messages.info(request,"Question is faild to submit",extra_tags='danger')
        else:
            messages.info(request,"Question is faild to submit",extra_tags='danger')

    form = FaqForms()

    faqs = FAQ.objects.all()
    solved  = faqs.filter(status='Solved').filter(is_active=True).count()
    total = faqs.count()
    percentage = (solved*100)//total
    context = {
        "form":form,
        "solved_questions":solved,
        "total_questions":total,
        "percentage_solved":percentage,
        'faqs':faqs.filter(is_active = True).order_by('-updated_at'),
        'post_message':post_message,
    }
    
    return render(request,'askQuestions.html',context=context)

def answerQuestions(request):
    global post_message
    if not request.user.is_authenticated or not is_superuser(request.user):
        return redirect('/admin/login/?next=/answer-questions/')
    
    post_message = False
    if request.method == "POST":
        question_id = request.POST.get('question_id',None)
        answer = request.POST.get('answer',None)
        notify_to = request.POST.get('notify',False)

        notify_to = True if notify_to == "True" else False

        print("The answer is :",answer,"!")
        full_url = request.build_absolute_uri('/')[:-1]  # Removes trailing slash


        try:
            if answer.strip() is None or answer.strip() == "":
                raise ValueError("answer not found")
                
            question = FAQ.objects.get(id=question_id)
            question.answer = answer
            question.status = "Solved"
            question.is_active = True
            question.updated_at = datetime.now()
            question.save()

            if question.email is not None:
                if notify_to:
                    SendAnswerMail(question.question,service=question.service,answer_url=f"{full_url}",question_id = question_id,user_email = question.email)
                    question.notified = notify_to
                    question.save()


            messages.success(request=request, message='The Question is answered',extra_tags="success")
        except FAQ.DoesNotExist:
            messages.info(request=request,message='The Question is failed to answer',extra_tags="danger")
        
        except ValueError as v:
            messages.info(request=request, message='answer not found',extra_tags="danger")
        except Exception as v: 
            messages.info(request=request, message=v,extra_tags="danger")

        post_message = True
    

    faqs = FAQ.objects.all()
    solved  = faqs.filter(status='Solved').filter(is_active = True).count()
    total = faqs.count()
    percentage = (solved*100)//total
    pending_questions = faqs.filter(status="Panding").order_by('-created_at')
    answered_questions_list = faqs.filter(status='Solved').order_by('-updated_at')
    archived_questions_list = faqs.filter(status='Archive').order_by('-updated_at')
    context = {
        "solved_questions":solved,
        "total_questions":total,
        "percentage_solved":percentage,
        'faqs':faqs,
        "pending_questions":pending_questions,
        "answered_questions_list":answered_questions_list,
        "archived_questions_list":archived_questions_list,
        'post_message':post_message,
    }

    return render(request,'answerQuestions.html',context=context)

def questionAction(request,n,action):
    
    question = FAQ.objects.get(id=n)

    print(f"the question is:{n}: action :{action}: object :{question}:")

    if question is not None:
        if action == 'delete':
            FAQ.objects.get(id=n).delete()
            messages.add_message(request=request,level=1, message='The Question is delete',extra_tags="success")

        elif action == "archive":
            question.status = "Archive"
            messages.add_message(request=request,level=1, message='The Question is archived',extra_tags="success")

        elif action == "retrive":
            if question.answer:
                question.status = "Solved"
            else:
                question.status = "Panding"
            messages.add_message(request=request,level=1, message='The Question is retrived',extra_tags="success")

        elif action == "active":
            question.is_active = True
            messages.add_message(request=request,level=1, message='The Question is ative now',extra_tags="success")
        
        elif action == "inactive":
            question.is_active = False
            messages.add_message(request=request,level=1, message='The Question is inacive now',extra_tags="success")

        elif action == "update":
            question.is_active = False
            question.status = "Panding"
            question.answer = ""
            question.updated_at = datetime.now()
            messages.add_message(request=request,level=1, message='The Question is update now',extra_tags="success")
        
        else:
            messages.add_message(request=request,level=2,message='The Question is not found',extra_tags="danger")
    else:
        print("question is not found")

    if action != 'delete':
        question.save()
        
    tab = request.GET.get('tab') or 1
    # return redirect('answers',{'tab': tab})
    base_url = reverse('answers')  # Make sure 'answers' is a valid URL name

    # Append query parameters manually
    query_params = {'tab': tab}
    final_url = f"{base_url}?{urlencode(query_params)}"

    # Use the generated URL
    return redirect(final_url)

def userAnswer(request,id):
    try:
        faq = FAQ.objects.get(id=id)
    except FAQ.DoesNotExist as e:
        faq = None

    return render(request,'user_answer.html',{'answer':faq})


def SendQuestionMail(question,service,answer_url):
     # Render the email template with dynamic data
    email_html_content = render_to_string("questions_email.html", {
        "question_text": question,
        "answer_url": answer_url,
        "service":service,
    })

    email_message = EmailMessage(
        subject=f"New Question Alert",
        body=email_html_content,
        from_email=formataddr(("Horizon Co&So", settings.EMAIL_HOST_USER)),  
        to=[settings.ADMIN_EMAIL],
    )

    email_message.content_subtype = "html"
    email_message.send()

def SendAnswerMail(question,service,answer_url,question_id,user_email):
     # Render the email template with dynamic data
    email_html_content = render_to_string("user_answer_email.html", {
        "question_text": question,
        "answer_url": answer_url,
        "service":service,
        "question_id":question_id,
    })

    email_message = EmailMessage(
        subject=f"Your Question Has Been Answered",
        body=email_html_content,
        from_email=formataddr(("Horizon Co&So", settings.EMAIL_HOST_USER)),  
        to=[user_email],
    )

    email_message.content_subtype = "html"
    email_message.send()
