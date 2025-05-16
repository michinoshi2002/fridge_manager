from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Item
import openai
import datetime

# OpenAI API key setting (not used)
openai.api_key = 'your_openai_api_key'

@login_required
# Main page: list of fridge items
def index(request):
    items = Item.objects.filter(user=request.user)
    return render(request, 'refrigerator/index.html', {'items': items})

# Sign up (user registration)
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        # Check for duplicate username
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('signup')
        # Required input check
        if not username or not password:
            messages.error(request, "Username and password are required")
            return redirect('signup')
        # Password match check
        if password != password2:
            messages.error(request, "Passwords do not match")
            return redirect('signup')
        # Create user
        user = User.objects.create_user(username=username, password=password)
        user.save()
        messages.success(request, "User created successfully")
        return redirect('login')
    else:
        return render(request, 'refrigerator/signup.html')

# Login
# Function name is login_view (to avoid conflict with Django's login function)
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')
    else:
        return render(request, 'refrigerator/login.html')

# Logout
# Always return an HttpResponse
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('login')

# Add item
@login_required
def add_item(request):
    if request.method == 'POST':
        item_name = request.POST.get('item_name')
        item_quantity = request.POST.get('item_quantity')
        current_date = datetime.datetime.now().date()
        if item_name and item_quantity:
            user = User.objects.get(username=request.user.username)
            # Prevent duplicate item names for the same user
            if Item.objects.filter(user=user, name=item_name).exists():
                messages.error(request, "Item already exists")
            else:
                item = Item(user=user, name=item_name, quantity=item_quantity, added_on=current_date)
                item.save()
                messages.success(request, "Item added successfully")
        return redirect('index')
    return redirect('index')

# Delete item
@login_required
def delete_item(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        try:
            item = Item.objects.get(id=item_id)
            item.delete()
        except Item.DoesNotExist:
            pass
    return redirect('index')

# Update item quantity
@login_required
def update_item_quantity(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        new_quantity = request.POST.get('new_quantity')
        try:
            item = Item.objects.get(id=item_id)
            item.quantity = new_quantity
            item.save()
        except Item.DoesNotExist:
            pass
    return redirect('index')

# Clear all items
@login_required
def clear_all_items(request):
    if request.method == 'POST':
        Item.objects.all().delete()
    return redirect('index')

# --- Below are unimplemented features such as recipe suggestions ---
# def suggest_recipes(request):
#     if request.method == 'POST':
#         item_names = request.POST.getlist('items')
#         prompt = f"Suggest recipes using the following ingredients: {', '.join(item_names)}"
#
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "user", "content": prompt}
#             ]
#         )
#         
#         recipes = response['choices'][0]['message']['content']
#         return render(request, 'refrigerator/recipes.html', {'recipes': recipes})
#     
#     return JsonResponse({'error': 'Invalid request'}, status=400)

# def recipes(request):
#     # Temporary recipe list
#     recipes_list = [
#         {"title": "Omelette", "ingredients": ["Eggs", "Milk", "Salt"]},
#         {"title": "Salad", "ingredients": ["Lettuce", "Tomato", "Cucumber"]},
#     ]
#     return render(request, "refrigerator/recipes.html", {"recipes": recipes_list})