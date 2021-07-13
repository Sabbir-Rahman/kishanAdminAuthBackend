from django.shortcuts import render
from users.models import OTP, User

# Create your views here.
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .email_wrappers import Util
from django.http import response
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User,OTP
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
from rest_framework import generics, serializers,status
from .serializers import userSerializer
import re
from .sms_wrappers import send_sms_twilio
from .utils import generate_referral_code


# http://127.0.0.1:8000/sms/send/
@api_view(['POST'])
def register(request):
    
    # Make a regular expression
    # for validating an Email
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    input = request.POST['input']
    password = request.POST['password']

    if(re.match(regex,input)):

        email = input
        user_obj = User.objects.filter(email=email)
        if user_obj.exists():
            return Response({'email':'User already exist'}, status=status.HTTP_400_BAD_REQUEST)
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
        phone_no = input
        user_obj = User.objects.filter(phone=phone_no)
        if user_obj.exists():
            return Response({'email':'User already exist'}, status=status.HTTP_400_BAD_REQUEST)
        

        otp_code = generate_referral_code()
        user_obj = User.objects.create(phone=phone_no,password=make_password(password))

        otp_obj = OTP.objects.filter(phone_or_email=phone_no)
        if otp_obj.exists():
            otp_obj = OTP.objects.get(phone_or_email=phone_no)
            otp_obj.otp_code=otp_code
            otp_obj.save()

        else:
            otp_create = OTP.objects.create(phone_or_email=input,otp_code=otp_code)

        # response_sms = send_sms_twilio(phone_no,otp_code)
       
        res = {
            'response_sms_otp' : otp_code,
            'message': 'Sms send to '+ str(phone_no)
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

#verify phone_otp
@api_view(['POST'])
def verify_phone_otp(request):

    phone_no = request.POST['phone_no']
    otp = request.POST['otp']

    otp_obj = OTP.objects.filter(phone_or_email=phone_no)

    if otp_obj.exists():
        otp_obj = OTP.objects.get(phone_or_email=phone_no)
        ''
        if(otp_obj.otp_code==otp):
            user = User.objects.get(phone = phone_no)
            if not user.verified:
                user.verified = True
                user.save()
            return Response({'message':'Account Verified'}, status=status.HTTP_200_OK)

        else:
            return Response({'message':'Wrong otp please enter correct one'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response({'message':'You have no otp with this number'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def login(request):
    
    # Make a regular expression
    # for validating an Email
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    input = request.POST['input']
    password = request.POST['password']

    if(re.match(regex,input)):

        email = input
        user_obj = User.objects.filter(email=email)
        if user_obj.exists():
            user_obj = User.objects.get(email=email)
            if (user_obj.verified==False):
                return Response({'message':'Please verify account first'})

            if(user_obj.password==check_password(password)):
              token = RefreshToken.for_user(user=user_obj).access_token
              return Response({'message':'Welcome '+str(email),'token':str(token)}, status=status.HTTP_200_OK)
            else:
              return Response({'message':'Password not matched'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':'User not found'}, status=status.HTTP_400_BAD_REQUEST)

        
    else:
        phone_no = input
        user_obj = User.objects.filter(phone=phone_no)

        if user_obj.exists():
            user_obj = User.objects.get(phone=phone_no)
            if (user_obj.verified==False):
                return Response({'message':'Please verify account first'})

            if(check_password(password,user_obj.password)):
              token = RefreshToken.for_user(user=user_obj).access_token
              return Response({'message':'Welcome '+str(phone_no),'token':str(token)}, status=status.HTTP_200_OK)
            else:
              return Response({'message':'Password not matched'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':'User not found'}, status=status.HTTP_400_BAD_REQUEST)
