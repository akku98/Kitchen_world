# to make : if user is , staff user they can also add their own recipes also
import stripe
from stripe.api_resources import source
from .forms import *
from django.http.response import HttpResponse ,HttpResponseRedirect
from django.shortcuts import render
from django.http import *
from .models import *
from .models import Cart,OrdersModel
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login,logout
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
import time
from .utils import IdGenerator
from django.contrib.auth.decorators import login_required
from localflavor.in_.in_states import STATE_CHOICES
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

try:
    stripe_pub = settings.STRIPE_PUBLISHABLE_KEY
    stripe_secret = settings.STRIPE_SECRET_KEY
except Exception as e:
    print(str(e))
    raise NotImplementedError(str(e))    

stripe.api_key = stripe_secret

# -----------------------------------------HOME---------------------------------------------------
def Home(request):
    pro = BestSeller.objects.order_by('-date_added')[0:3]    # best sellers
    recipes = BestRecipes.objects.order_by('-date_added')[0:3]  # best recipes
    print(recipes)
    print(pro)
    return render(request, 'home.html',{'best_seller':pro , 'best_recipes':recipes})

# ----------------------------------------SIGNUP--------------------------------------------------
@csrf_exempt
def signup(request):
    if request.method =='POST':
        form = user_form(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            user_name = form.cleaned_data['user_name']
            user_email = form.cleaned_data['user_email']
            user_pass = form.cleaned_data['user_pass']
            user_count = User.objects.filter(email = user_email).count()
            if user_count > 0 :
                messages.success(request, 'User with this email is already been registered !!')
            else:   
                password = make_password(user_pass)  # pass encryption
                User.objects.create(password = password,username = user_name,first_name=first_name,last_name = last_name,email=user_email)
                messages.success(request, 'You are successfully registered!!')
            return HttpResponseRedirect(reverse('myhome'))
        else:
            return render(request, "home.html", {'form': form})    

#----------------------------------------LOGIN---------------------------------------------------
# custom user verification (user login) ----using auth user table
@csrf_exempt
def login_view(request):
    if request.method =='POST'  :
        print('in post')
        form = LoginForm(request.POST)
        if form.is_valid():
            your_name = form.cleaned_data['username']  
            your_password = form.cleaned_data['password']   
            user1 = authenticate(request, username=your_name, password=your_password)  # here username and password are the column name of authuser table
            print(user1)
            if user1 is not None:
                login(request,user1)  # creates session 
                request.session['user_logged'] = 'logged'   # creating another key value pair in session dict
                print("in custom login")
                print(request.session['user_logged'])
                return HttpResponseRedirect(reverse('myhome'))
            else:
                return HttpResponseRedirect(reverse('my-login') + '?loginfail=true')    # redirect to login form page (here reverse is neccessary to use name instead of url path)

        else:
            return render(request, "signin.html", {'form': form})
    
    else:
        print("in get")
        form = LoginForm()

        return render(request, 'signin.html', {'form': form})


# logout
def logout_view(request):
    print("in logout")
    logout(request)   # session destroy
    if 'user_logged' in request.session:
        var=request.session['user_logged']
    else:
        var="session var deleted"
    print(var)
    return HttpResponseRedirect('/users/login')        

def About_page(req):
    return render(req,'about.html')

#-----------------------------------------------CONTACT--------------------------------
@csrf_exempt
def Contact_page(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            uname = form.cleaned_data['uname']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            desc = form.cleaned_data['desc']
            contact =Contact(user_name=uname,email=email,phone=phone,desc=desc)
            contact.save()
            messages.success(request, 'Your message has been sent!!')
            return render(request,'home.html')    
        else:
            return render(request, "contact.html", {'form': form}) 
    else:
        print("in get")
        form = ContactForm()
        return render(request, 'contact.html', {'form': form})


# -----------------------------------PRODUCT----------------------------------------------
def products_list(request,cata):
    pro = Products.objects.filter(Sub_cata = cata)
    paginator = Paginator(pro, 5) # 5 products in each page
    page = request.GET.get('page')
    try:
        posts = paginator.get_page(page)
       
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)

    print("page {} posts {} posts type tag {}".format(page,posts,type(posts)))
    return render(request,'products.html',{'pro': pro,'cata':cata ,'page': page,'posts': posts})

def Pro_details_page(req,slug):
    pro = Products.objects.get(slug = slug)
    return render(req,'pro_details.html',{'pro':pro})

def products_filter(req):

    minprice = req.GET.get('min')
    maxprice = req.GET.get('max')
    cata = req.GET.get('cata')
    
    pro_filter = Products.objects.filter(Sub_cata=cata,pro_price__range=(minprice,maxprice))
    
    if pro_filter == "None":
        messages.success(req, 'No Products Found')
        return HttpResponse(reverse('product_filter')) 

    paginator = Paginator(pro_filter, 5) # 5 products in each page
    page = req.GET.get('page')
    try:
        posts = paginator.get_page(page)
       
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)

    print("page {} posts {} posts type tag {} pro_filter {}".format(page,posts,type(posts),pro_filter))
    return render(req,'products_filter.html',{'cata':cata ,'page': page,'posts': posts})


#--------------------------------------RECIPE----------------------------------------------
def Recipe_page(request,cata):
    recipe = Recipes.objects.filter(catagory = cata)
    paginator = Paginator(recipe, 6) 
    page = request.GET.get('page')
    try:
        posts = paginator.get_page(page)
       
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)


    return render(request,'recipes.html',{'recipe':recipe,'cata':cata,'posts':posts})

#-------------------------------------CART-------------------------------------------------------
def CartView(req):
    try:
        the_id = req.session['cart_id']
        cart = Cart.objects.get(id=the_id) 
    except:
        the_id =None  # logged out
    if the_id  :
        new_total =0.00
        for item in cart.cartitem_set.all(): # details of the specific cartid
            line_total = new_total + (item.products.pro_price * item.quantity)
            new_total = line_total

        req.session['items_total'] = cart.cartitem_set.count()    
        cart.total = new_total
        cart.save() 
        context = {'cart':cart}   
    else:
        empty_message = 'Your cart is empty, Please keep shopping!'    
        context = {'empty':True , 'empty_message':empty_message}  

    template = 'cart_page.html'
    return render(req,template,context)

def remove_from_cart(req,id):
    try:
        the_id = req.session['cart_id']
        cart = Cart.objects.get(id=the_id)
    except:
        return HttpResponseRedirect(reverse('cart')) 

    cartitem = CartItem.objects.get(id = id)
    #cartitem.delete()  # it will delete the pro from database (table cartitem)
    cartitem.cart = None  # it will not delete the product from database , update the pro cartid as NULL
    cartitem.save()
    #send success msg 
    return HttpResponseRedirect(reverse('cart'))    

# after clicking addtocart :
def update_cart(req,slug):   # work for both registered and non registered , for non-registered it will simply store the products to same cartid which is created once registered user is logged out
     # req.session.set_expiry(120000)

    try:
        qty=req.GET.get('qty')
        update_qty = True
    except:
        qty = None
        update_qty = False

    try:                                   # each user will have separate cart id
        the_id = req.session['cart_id']   # if user is logged in and have cartid ,then add item to same cart_id
    except:                             
        new_cart = Cart()               # if user is loggedin but does'nt have cartid , or once the user is loggedout it will create new empty row in cart table for non-registered or registered user
        new_cart.save()                               # as their is no session[cart_id] once user is logged out
        req.session['cart_id'] = new_cart.id
        the_id = new_cart.id
    print(the_id) 
    cartid = Cart.objects.get(id=the_id)

    try:
        pro = Products.objects.get(slug = slug)
    except Products.DoesNotExist:
        pass
    
    cart_item , created = CartItem.objects.get_or_create(cart=cartid,products=pro)
    if created:
        print('yeah')  
    
    if update_qty and qty:
        if int(qty) <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = qty
            cart_item.save()
    else:
        pass        

    """ if not cart_item in cart.items.all() :
        cart.items.add(cart_item)  # many to many field
    else:
        cart.items.remove(cart_item)
 """   

    return HttpResponseRedirect(reverse('cart')) # url name='cart'


#-------------------------------------ORDER----------------------------------------------------------------
def Order(req):
    
    if req.user :
        user_id = req.user  # user id in session
        user_order = OrdersModel.objects.latest('id')  # get the orders of the respected user ( latest order id )
        cart_id = Cart.objects.latest('id')
        id = cart_id.id
        cartitems = CartItem.objects.filter(cart =id)
    else:
        return HttpResponseRedirect(reverse('my-login'))
    
    context ={'user':user_order,'products':cartitems}
    template = 'user.html'
    return render(req,template,context)


# ---------------------------CHECKOUT-------------------------------------------------------------------------------
@login_required(login_url='/users/login/')     # if user not logged in ,redirect to login page
def CheckoutView(req):
    try:
        the_id = req.session['cart_id']
        cart = Cart.objects.get(id=the_id)
    except:
        the_id = None
        return HttpResponseRedirect(reverse('cart'))  

    try:
        new_order =  OrdersModel.objects.get(cart = cart)  
    except OrdersModel.DoesNotExist:
        new_order = OrdersModel()
        new_order.cart = cart
        new_order.user = req.user
        new_order.ord_id = IdGenerator()
        new_order.save() 
        return HttpResponseRedirect(reverse('cart'))          
    except:
        new_order =None
        return HttpResponseRedirect(reverse('cart'))  
    final_amount = 0     
    if new_order is not None:    
        new_order.subtotal = cart.total
        new_order.save()
        final_amount = new_order.get_final_amount()
    
    address_form = UserAddressForm()
    
    """ try:
        address_added = req.GET.get("addu")
        print(address_added)
    except:
        address_added = None
    if address_added is None:       
        address_form = UserAddressForm()        # form for user address
    else:
        address_form = None """

    current_add = UserAddress.objects.filter(user = req.user.id)  
    billing_add = UserAddress.objects.get_billing_address(user = req.user.id)  
    print(billing_add)

    if req.method == "POST":                   # for stripe International or Indian  payment
        try:
            user_stripe = req.user.userstripe.stripe_id
            customer = stripe.Customer.retrieve(user_stripe)
            print(customer)
        except:
            customer = None
            pass
        if customer is not None:
            
            token = req.POST['stripeToken']
    
            try:  
                billing_a = req.POST['billing_address']    
                shipping_a = req.POST['shipping_address']  
            except:
                billing_a = None
                shipping_a = None 
                   
            
            if billing_a is not None: 
                billing_instance = UserAddress.objects.get(id=billing_a)
            else:
                billing_instance = None

            if shipping_a is not None: 
                shipping_instance = UserAddress.objects.get(id=shipping_a)
            else:
                shipping_instance = None    

            #card = stripe.customers.cards.create(card=token)            
            charge = stripe.Charge.create(                         # user card activation
                amount = int(final_amount * 100),
                currency = "inr",
                #card = card ,
                source = token,
                description = "Charge for %s" %(req.user.username),
                
                
                )
            #print(card)
            print(charge)
            if charge['captured'] :
                new_order.status = 'Finished'    # if payment success delete the cartid
                new_order.shipping_address = shipping_instance
                new_order.billing_address = billing_instance
                new_order.save()    
                del req.session['cart_id']
                del req.session['items_total']
                messages.success(req, " Thank You for shopping !! It has been completed")
                return HttpResponseRedirect(reverse('user-order'))  
    
    
    context = {'address_form':address_form ,
                'current_addresses':current_add,
                'billing_addresses':billing_add,
                'state_choices':STATE_CHOICES ,
                'order':new_order,
                'stripe_pub': stripe_pub
             }
    template = 'checkout.html'
    return render(req,template, context)        

@csrf_exempt
def add_user_address(req):
    try:
        redirect = req.GET.get('redirect')  # getting through qstring in checkout.html form
    except:
        redirect = None  
    address_form = UserAddressForm(req.POST)      
    if req.method == 'POST':         
        if address_form.is_valid():
            """ address = address_form.cleaned_data['address']
            address2 = address_form.cleaned_data['address2']
            city = address_form.cleaned_data['city']
            state = address_form.cleaned_data['state']
            country = address_form.cleaned_data['country']
            pincode =address_form.cleaned_data['pincode']
            phoneno = address_form.cleaned_data['phoneno']           
            user_address =UserAddress(
                                       address=address,
                                       address2=address2,
                                       city=city,
                                       state=state,
                                       country=country,
                                       pincode = pincode,
                                       phoneno = phoneno,
                                       
                                      )                          
            user_address.user = req.user                          
            user_address.save()  """
            add_type = address_form.cleaned_data['address_type']

            if add_type == 'Shipping_Address' :
                new_address = address_form.save(commit=False)  # for forms.Model
                new_address.user = req.user
                new_address.shipping = 1
                new_address.save()
                default_address , created = UserDefaultAddress.objects.get_or_create(user=req.user)
                default_address.shipping = new_address
                default_address.save()


            if add_type == "Billing_Address":
                new_address = address_form.save(commit=False)  # for forms.Model
                new_address.user = req.user
                new_address.billing = 1
                new_address.save()
                default_address , created = UserDefaultAddress.objects.get_or_create(user=req.user)
                default_address.billing = new_address
                default_address.save()      
               

            if redirect is not None:
                return HttpResponseRedirect(reverse(str(redirect)))  # redirect to checkout page
            else:
                return HttpResponse("rediret not found")  
        else:
            """ return HttpResponseRedirect(reverse('checkout'))   """ 
            return HttpResponse("Form not valid")
    else:
        return Http404

def user_account(req):
    user_id = req.user
    user_default_address = UserDefaultAddress.objects.filter(user=user_id)
    user_orders = OrdersModel.objects.filter(user = user_id)
         
    if req.method == 'POST':  
        address_form = UserAddressForm(req.POST)        
        if address_form.is_valid():
            add_type = address_form.cleaned_data['address_type']

            if add_type == 'Shipping_Address' :
                new_address = address_form.save(commit=False)  # for forms.Model
                new_address.user = req.user
                new_address.shipping = 1
                new_address.save()
                default_address , created = UserDefaultAddress.objects.get_or_create(user=req.user)
                default_address.shipping = new_address
                default_address.save()


            if add_type == "Billing_Address":
                new_address = address_form.save(commit=False)  # for forms.Model
                new_address.user = req.user
                new_address.billing = 1
                new_address.save()
                default_address , created = UserDefaultAddress.objects.get_or_create(user=req.user)
                default_address.billing = new_address
                default_address.save()      
            
            return render(req, 'account.html',{'user_add':user_default_address,'address_form':address_form,'orders':user_orders})    
        else:
            messages.success(req, "Form Not Valid")
            return HttpResponseRedirect(reverse('add_address'))
            
    else:
        form = UserAddressForm()
        return render(req, 'account.html',{'user_add':user_default_address,'address_form':form,'orders':user_orders})
    