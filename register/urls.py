from django.urls import path
from .views import (
    login,
    register,
    verify_email,
    view_user,
    verify_phone_otp
)


urlpatterns = [   
    path('register/', register),
    path('verify/', verify_email, name="email-verify"),
    path('view/', view_user),
    path('verifyphoneotp/', verify_phone_otp),
    path('login/', login)
    
]