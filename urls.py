"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from kwapp import views
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #-------------------------------Admin------------------------------
    path('admin/', admin.site.urls),

    #---------------------------Home----------------------------------
    path('home/',views.Home,name='myhome'),

    #--------------------------Register------------------------------
    path('signup/',views.signup,name='signup_page'),

    #-------------------------Products-------------------------------
    path('products_list/<str:cata>/',views.products_list,name='pro_list'),
    path('pro_details/<slug:slug>/',views.Pro_details_page,name='prodetails'),
    path('products_filter/',views.products_filter,name='pro_filter'),
    #------------------------Contact us--------------------------------
    path('contact/',views.Contact_page,name='contactus'),

    #----------------------Recipes-------------------------------------
    path('recipes/<str:cata>/',views.Recipe_page,name='recipes'),

    #---------------------about us--------------------------------------
    path('about/',views.About_page,name='aboutus'),

    #-------------------Login-------------------------------------------
    path('users/login/',views.login_view,name='my-login'),
    path('users/logout/',views.logout_view,name='my-logout'),
    path('userpage/', TemplateView.as_view(template_name='mypage.html'), name='my-page'),

    #-----------------Cart----------------------------------------------
    path('cart/',views.CartView,name='cart'),
    path('cart/<int:id>',views.remove_from_cart,name='cart-remove'),
    path('cart/<slug:slug>',views.update_cart,name='cart-update'),

    # --------------------Orders and Checkout-----------------------------
    path('orders/',views.Order,name='user-order'),
    path('checkout/',views.CheckoutView,name='checkout'),
    path('ajax/add_user_address/',views.add_user_address,name='ajax_user_address'),

    path('accounts/address/add/',views.add_user_address,name='add_address'),

    path('account/',views.user_account,name="u_account")
] + static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)
