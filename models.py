from datetime import date
from django.db import models
from django.db.models.fields import AutoField, TextField
from django.db.models.fields.related import ForeignKey
from django.forms.fields import BooleanField, CharField
from django.utils import timezone
from django.contrib.auth.models import User
import stripe
from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from decimal import Decimal
from localflavor.in_.in_states import STATE_CHOICES  # addintional library to show various states in dropdown

# if we want to add more states---
""" NEW_STATES = (
    ('AB','AB state'),
    ('BC','BC state')
)

NEW_STATES += STATE_CHOICES """

try:
    tax_rate = settings.DEFAULT_TAX_RATE
except Exception as e:
    print(str(e))
    raise NotImplementedError(str(e))     


#about us
#all home contents through database
class Contact(models.Model):
    contact_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    phone = models.IntegerField()
    desc = models.TextField(max_length=50)

class Recipes(models.Model):
    RCATA_CHOICES = [('BrunchandBreakfast','BrunchBreakfast'),
                    ('Lunch','Lunch'),
                    ('Dinner','Dinner'),
                    ('Appitizers','Appitizers'),
                    ('Healthy','Healthy'),
                    ('Drinks','Drinks')
                    ]

    recipe_id = models.AutoField(primary_key=True)
    recipe_name = models.CharField(max_length=50)
    desc =  models.TextField(max_length=1000,null=True,blank=True)
    youtube_link = models.URLField(max_length = 200)
    catagory = models.CharField(max_length=100,choices=RCATA_CHOICES)
    Recipe_by = models.CharField( max_length=50)
    image = models.ImageField( upload_to='recipe_images', default="")
    date_added = models.DateField(default =date.today)
    #img

class BestRecipes(models.Model):
    br_id = models.AutoField(primary_key=True)
    recipes = models.ForeignKey(Recipes, on_delete=models.CASCADE) 
    date_added = models.DateField(default =date.today)

class Products(models.Model):
    STATUS_CHOICES = [('In Stock','In Stock'),('Sold Out','Sold Out')]
    CATA_CHOICES = [('Kitchen','Kitchen'),('Spices','Spices')]
    SUBCATA_CHOICES = [
        ('Utensils','Utensils'),
        ('Appliances','Appliances'),
        ('Decoratives','Decoratives'),
        ('Indian','Indian'),
        ('Continental','Continental'),
        ('Italian','Italian')
        ]

    pro_id = models.AutoField(primary_key=True)
    pro_name = models.CharField(max_length=200)
    pro_price = models.IntegerField()
    desc = models.TextField(max_length=1000,null=True,blank=True)
    catagory = models.CharField( max_length=50,choices=CATA_CHOICES)
    Sub_cata = models.CharField( max_length=50,choices=SUBCATA_CHOICES)
    Status = models.CharField(max_length=50,null = True,choices=STATUS_CHOICES)
    slug = models.SlugField(unique=True)
    image = models.ImageField( upload_to='product_images', default="")
    # img

    def __unicode__(self):
        return self.pro_name
  
    class Meta:
        unique_together = ('pro_name','slug') # both will be unique , can't be duplicate


class Orders(models.Model):
    ord_id = models.AutoField(primary_key=True)
    pro_cus = models.ManyToManyField(Products)
    cus_id = models.ForeignKey(User, on_delete=models.CASCADE) 
    total_amount = models.IntegerField(null=True,blank=True)

class BestSeller(models.Model):
    bs_id = models.AutoField(primary_key=True)
    products = models.ForeignKey(Products,  on_delete=models.CASCADE)
    date_added = models.DateField(default =date.today)      

class Cart(models.Model):
    total = models.DecimalField(max_digits=50,decimal_places=2,default=0.00)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField( auto_now=True, auto_now_add=False)
    activate = models.BooleanField(default=True)
    def __unicode__(self):
        return "Cart Id: %s" %(self.id)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,null=True,blank=True)
    products = models.ForeignKey(Products,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    line_total = models.DecimalField( default=10.99,max_digits=50, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(default=timezone.now)
    def __unicode__(self):
        try:
            return str(self.cart.id)
        except:
            return self.products.pro_name    


class UserStripe(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_id = models.CharField( max_length=120,null = True,blank=True)    
    
    def __unicode__(self):
        return str(self.stripe_id)



class UserAddressManager(models.Manager):
    def get_billing_address(self,user):
        return super().filter(billing=True).filter(user = user)   # or super(UserAddressManager,self)

class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=120)
    address2 = models.CharField(max_length=120,null=True,blank=True)
    city = models.CharField( max_length=120)
    state = models.CharField( max_length=120 ,choices = STATE_CHOICES)
    country = models.CharField( max_length=120)
    pincode = models.CharField( max_length=25)
    phoneno = models.CharField( max_length=12)
    shipping = models.BooleanField(default=True)
    billing = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return str(self.user.username)

    def get_address(self):
        return "%s, %s, %s, %s, %s " %(self.address , self.city , self.state,self.country,self.pincode)

    objects= UserAddressManager()    

    class Meta:
        ordering = ['-updated' , '-timestamp'] 

class UserDefaultAddress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # if related name is used then don't need to use _set , and if there are two same foreign key in same table error will not occur 
    shipping = models.ForeignKey(UserAddress, on_delete=models.CASCADE , null= True,blank=True , related_name="user_address_shipping_default")  
    billing =  models.ForeignKey(UserAddress, on_delete=models.CASCADE , null= True,blank=True , related_name="user_address_billing_default") 

    def __unicode__(self):
        return str(self.user.username)

class OrdersModel(models.Model):
    STATUS_CHOICES = [('Started','Started'),('Abandon','Abandon'),('Finished','Finished')]
    
    #address---
    ord_id = models.CharField(max_length=120 , default='ABC',unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE)
    status = models.CharField(max_length=120,choices=STATUS_CHOICES,default='Started')
    shipping_address = models.ForeignKey(UserAddress, on_delete=models.CASCADE, related_name="shipping_a",default=1)
    billing_address = models.ForeignKey(UserAddress, on_delete=models.CASCADE, related_name="billing_a",default=1)
    subtotal = models.DecimalField( default=10.99,max_digits=50, decimal_places=2)
    tax = models.DecimalField( default=0.00,max_digits=50, decimal_places=2)
    Finalprice = models.DecimalField( default=10.99,max_digits=50, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(default=timezone.now)
    def __unicode__(self):
        return str(self.ord_id)

    def get_final_amount(self):
        instance = OrdersModel.objects.get(id = self.id)  # get the id of object
        two_place = Decimal(10)** -2
        tax_rate_dec = Decimal("%s" %(tax_rate))
        sub_total_dec = Decimal(self.subtotal)  # cart total
        instance.tax =Decimal( tax_rate_dec * sub_total_dec ).quantize(two_place)
        instance.Finalprice = sub_total_dec + Decimal(instance.tax)   # final price including tax
        instance.save()
        return self.Finalprice      





#---------------------------------------------SIGNAL------------------------------------------------------------
stripe.api_key = settings.STRIPE_SECRET_KEY
User = User


""" def get_or_create_stripe(sender,user,*args,**kwargs) :     # creating stripeid after user logs in
    #print( sender)
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

user_logged_in.connect(get_or_create_stripe)   #if user logged in sends signal to the function """

def get_create_stripe(user):   # creating stripe id ,when user signups  
    new_user_stripe , created = UserStripe.objects.get_or_create(user = user)  # getting or creating  user
    if created:
        customer = stripe.Customer.create(         # creating customer
            email = str(user.email)
        )
        new_user_stripe.stripe_id = customer.id  # assigning the value of id from customer dictionary
        new_user_stripe.save()
    
def user_created(sender,instance,created,*args,**kwargs):  # reciver
    if created:
        get_create_stripe(instance) # calling the function to create stripeid
    print(sender)
    print(instance)
    print(created)
    # send email
post_save.connect(user_created,sender = User)    # confirmation signal when user is created(signup) in console