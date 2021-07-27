# for stripe use (payments)

import stripe
from .models import UserStripe
from django.conf import settings
from django.contrib.auth.signals import user_logged_in

stripe.api_key = settings.STRIPE_SECRET_KEY

def get_or_create_stripe(sender,user,*args,**kwargs) :
    #print( sender)
    print(user)
    print('something')
    try:
        user.userstripe.stripe_id    # if stripe_id exists
    except UserStripe.DoesNotExist:    
        customer = stripe.Customer.create(         # if not exists
            email = str(user.email)
        )
        new_user_stripe = UserStripe.objects.create(
            user = user,
            stripe_id = customer.id            # assigning the value of id from customer dictionary
        )
    except:
        pass  

user_logged_in.connect(get_or_create_stripe)   #if user logged in sends signal to the function