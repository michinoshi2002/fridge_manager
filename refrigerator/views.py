from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate as django_authenticate
from .models import Item, User
import openai
import datetime

# Set your OpenAI API key
openai.api_key = 'your_openai_api_key'

def index(request):
    if not request.session.get('logged_in'):
        return redirect('login')
    items = Item.objects.all()
    return render(request, 'refrigerator/index.html', {'items': items})

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == 'admin' and password == 'password':  # Dummy check
            request.session['logged_in'] = True
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')
    else:
        return render(request, 'refrigerator/login.html')

def logout(request):
    if request.method == 'POST':
        request.session['logged_in'] = False
        message = "Logged out successfully"
        return render(request, 'refrigerator/login.html', {'message': message})

def add_item(request):
    if request.method == 'POST':
        item_name = request.POST.get('item_name')
        item_quantity = request.POST.get('item_quantity')
        current_date = datetime.datetime.now().date()
        
        if item_name and item_quantity:
            user = User.objects.first()  # 仮のユーザー（本来はログインユーザーを使う）
            item = Item(user=user, name=item_name, quantity=item_quantity, date_of_purchase=current_date)
            item.save()
        return redirect('index')
    
    return redirect('index')

def delete_item(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        
        try:
            item = Item.objects.get(id=item_id)
            item.delete()
        except Item.DoesNotExist:
            pass
    
    return redirect('index')

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

def clear_all_items(request):
    if request.method == 'POST':
        Item.objects.all().delete()
    
    return redirect('index')

# Will do it later.

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
        
#         recipes = response['choices'][0]['message']['content']
#         return render(request, 'refrigerator/recipes.html', {'recipes': recipes})
    
#     return JsonResponse({'error': 'Invalid request'}, status=400)

# def recipes(request):
#     # 仮のレシピリスト
#     recipes_list = [
#         {"title": "オムレツ", "ingredients": ["卵", "牛乳", "塩"]},
#         {"title": "サラダ", "ingredients": ["レタス", "トマト", "きゅうり"]},
#     ]
#     return render(request, "refrigerator/recipes.html", {"recipes": recipes_list})