from django.shortcuts import render
from users.models import User

# Create your views here.
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .email_wrappers import Util
from django.http import response
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
from rest_framework import generics, serializers,status
from .serializers import userSerializer
import re


# http://127.0.0.1:8000/sms/send/
@api_view(['POST'])
def register(request):
    
    # Make a regular expression
    # for validating an Email
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    input = request.POST['email']
    password = request.POST['password']

    if(re.match(regex,input)):
        email = input
        user_obj = User.objects.create(email=email,password=make_password(password))

        #sending token for email verification
        token = RefreshToken.for_user(user=user_obj).access_token

        current_site = get_current_site(request).domain

        relative_link = reverse('email-verify')

        absurl = 'http://'+current_site+relative_link+"?token="+str(token)

        email_body = 'স্বাগতম\n'+ 'আপনাকে কিষাণে রেজিষ্ট্রেশন করার জন্য ধন্যবাদ। নীচের লিন্কে ক্লিক করে আপনার রেজিস্ট্রেশন ভেরিফাই করুন এবং ভেরিফাই এর পর পুনরায় লগ ইন করুন \n \n'+absurl+'\n\n ধন্যবাদান্তে\n-টিম কিষাণ'
        data ={'to_email':email,'email_body':email_body,'email_subject': 'Verify your email'}

        Util.send_email(data)
        
    

        res = {
            'message': 'Email send to '+ str(email),
        }
        return Response(res, status=200)
    else:
        phone = input
        res = {
            'message': 'OTP send to '+ str(phone),
        }
        return Response(res, status=200)


  
    
    

   

#verify email 
@api_view(['GET'])
def verify_email(request):
    token = request.GET.get('token')
  
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(id=payload['user_id'])
        

        if not user.verified:
            user.verified = True
            user.save()

        return Response({'বার্তা':'আপনার ইমেইল ভেরিফিকেশন সফল হয়েছে। অনুগ্রহ করে লগ ইন পেজ থেকে লগইন করুন।'},status=status.HTTP_200_OK)

    except jwt.ExpiredSignatureError as identifier:
       return Response({'email':'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
    except jwt.exceptions.DecodeError as identifier:
        return Response({'email':'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)



#verify email 
@api_view(['GET'])
def view_user(request):
    user = User.objects.all()
    serializer = userSerializer(user, many= True)
    return Response(serializer.data)
