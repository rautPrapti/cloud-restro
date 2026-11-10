from django.contrib import admin
from .models import Category,FoodItem,Order,OrderItem

admin.site.register(Category)
admin.site.register(FoodItem)
admin.site.register(Order)
admin.site.register(OrderItem)
