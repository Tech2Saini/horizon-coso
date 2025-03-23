from django.urls import path
from mfaauth.views import upload_mfa_qr,showAndUpdateOtp,get_otp,user_login,logOut_User,session_check
from django.views.generic import RedirectView
from django.urls import re_path
# from django.contrib.admin.views.decorators import staff_member_required

# @staff_member_required
# def custom_admin_action(request):
#     return HttpResponse("Custom button clicked!")

# urlpatterns = [
#     path('admin/custom-action/', custom_admin_action, name='your_custom_url_name'),
# ]


urlpatterns = [
    # path("",upload_mfa_qr,name='upload_mfa_qr'),
    path("upload-mfa/", upload_mfa_qr, name="upload_mfa_qr"),  # Admin-only upload page
    path("show-otp/", showAndUpdateOtp, name="show_otp"),  # Admin-only upload page
    path("get-otp/", get_otp, name="get_otp"),  # Admin-only upload page
    path("login/", user_login, name="mfa_login"),  # Admin-only upload page
    path("logout/", logOut_User, name="mfa_logout"),  # Admin-only upload page
    path('session_check/', session_check, name='session_check'),
    re_path('', RedirectView.as_view(url='/mfa/show-otp/', permanent=True)),

]
