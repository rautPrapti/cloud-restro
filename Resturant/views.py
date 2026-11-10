from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render,redirect,get_object_or_404
from django .contrib import messages
from decimal import Decimal
from .models import FoodItem,Category, Order, OrderItem

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import FoodItemSerializer

from .ai_service import get_food_recommendation



# Create your views here.
def home (request):
    return render(request, 'home.html')

def food_menu(request):
    foods= FoodItem.objects.filter(is_available=True)
    categories= Category.objects.all()

    search= request.GET.get('search')
    category_id=request.GET.get('category')

    if search:
        foods = foods.filter(name__icontains=search)

    if category_id:
        foods=foods.filter(category_id=category_id)

    return render(request, 'menu.html',{
        'foods': foods,
        'categories': categories
    })



def add_to_cart(request, food_id):
    if request.method == 'POST':
        food = get_object_or_404(
            FoodItem,
            id=food_id,
            is_available=True
        )

        cart = request.session.get('cart', {})
        food_id = str(food_id)

        cart[food_id] = cart.get(food_id, 0) + 1

        request.session['cart'] = cart
        request.session.modified = True

    return redirect('menu')


def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = Decimal('0.00')

    for food_id, quantity in cart.items():
        food = get_object_or_404(
            FoodItem,
            id=food_id
        )

        subtotal = food.price * quantity
        total += subtotal

        cart_items.append({
            'food': food,
            'quantity': quantity,
            'subtotal': subtotal
        })

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })


def update_cart(request, food_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        food_id = str(food_id)

        quantity = int(request.POST.get('quantity', 1))

        if food_id in cart:
            if quantity > 0:
                cart[food_id] = quantity
            else:
                cart.pop(food_id)

        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart')


def remove_from_cart(request, food_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        cart.pop(str(food_id), None)

        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart')


@login_required
def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart')

    cart_items = []
    total = Decimal('0.00')

    for food_id, quantity in cart.items():
        food = get_object_or_404(
            FoodItem,
            id=food_id,
            is_available=True
        )

        subtotal = food.price * quantity
        total += subtotal

        cart_items.append({
            'food': food,
            'quantity': quantity,
            'subtotal': subtotal
        })

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        if not customer_name or not phone or not address:
            return render(request, 'checkout.html', {
                'cart_items': cart_items,
                'total': total,
                'error': 'Please fill in all delivery details.'
            })

        with transaction.atomic():
            order = Order.objects.create(
                customer=request.user,
                customer_name=customer_name,
                phone=phone,
                address=address,
                total_price=total
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    food_item=item['food'],
                    quantity=item['quantity'],
                    price=item['food'].price
                )

        request.session['cart'] = {}

        return render(request, 'order_success.html', {
            'order': order
        })

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def my_orders(request):
    orders = Order.objects.filter(
        customer=request.user
    ).prefetch_related(
        'items__food_item'
    ).order_by('-created_at')

    return render(request, 'my_orders.html', {
        'orders': orders
    })


@api_view(['GET'])
def food_api(request):

    foods = FoodItem.objects.filter(is_available=True)

    serializer = FoodItemSerializer(foods, many=True)

    return Response(serializer.data)



@api_view(['GET'])
def food_detail_api(request, food_id):

    try:
        food = FoodItem.objects.get(
            id=food_id,
            is_available=True
        )

    except FoodItem.DoesNotExist:
        return Response(
            {'error': 'Food item not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = FoodItemSerializer(food)

    return Response(serializer.data)

def ai_recommendation(request):

    recommendation = None
    error = None

    if request.method == 'POST':

        preference = request.POST.get('preference', '').strip()

        if preference:

            foods = FoodItem.objects.filter(
                is_available=True
            ).select_related('category')

            try:
                recommendation = get_food_recommendation(
                    preference,
                    foods
                )
            except Exception as e:
                import traceback
                traceback.print_exc()
                error = f"AI Error: {e}"

        else:
            error = "Please enter your food preference."

    return render(
        request,
        'ai_recommendation.html',
        {
            'recommendation': recommendation,
            'error': error,
        }
    )

