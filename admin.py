from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Products)
admin.site.register(Recipes)
admin.site.register(UserStripe)
admin.site.register(UserAddress)
admin.site.register(BestRecipes)
admin.site.register(BestSeller)

class CartAdmin(admin.ModelAdmin):
    class Meta:
        model = Cart

admin.site.register(Cart,CartAdmin)
