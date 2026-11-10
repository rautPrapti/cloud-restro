from django.urls import path
from . import views

urlpatterns = [
    path('menu/', views.food_menu, name='menu'),
    path('add-to-cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='cart'),
    path('update-cart/<int:food_id>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:food_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('api/foods/', views.food_api, name='food_api'),
    path('api/foods/<int:food_id>/',views.food_detail_api,name='food_detail_api'),
    path('ai-recommendation/',views.ai_recommendation,name='ai_recommendation'),
]