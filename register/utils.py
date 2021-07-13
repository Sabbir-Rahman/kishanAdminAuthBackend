from users.models import User
import uuid
import string
import random
from datetime import datetime, timedelta
from rest_framework.authtoken.models import Token

def generate_referral_code():

    # run loop until the define length 
    first_string_length = 2
    middle_digit_length = 2
    last_string_length = 2
    referral_code =  ''.join((random.choice(string.ascii_letters) for x in range(first_string_length))) 
    referral_code +=  ''.join((random.choice(string.digits) for x in range(first_string_length))) 
    referral_code +=  ''.join((random.choice(string.ascii_letters) for x in range(first_string_length))) 
    return referral_code