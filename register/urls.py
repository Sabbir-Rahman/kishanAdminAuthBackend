from django.urls import path
from .views import (
    register,
    verify_email,
    view_user
)


urlpatterns = [   
    path('register/', register),
    path('verify/', verify_email, name="email-verify"),
    path('view/', view_user),
    
]