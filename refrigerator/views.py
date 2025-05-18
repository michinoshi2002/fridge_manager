from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Item, Recipes
import openai
import datetime
import json
import re
import os
from openai import AuthenticationError

@login_required
def index(request):
    """
    Main page: Shows fridge items and handles recipe suggestions via OpenAI API.
    """
    items = Item.objects.filter(user=request.user)
    recipes = []
    # Use temporary API key from session if present, else use environment/global key
    api_key = request.session.get('temp_openai_api_key') or os.environ.get('OPENAI_API_KEY')
    if request.method == 'POST' and 'suggest_recipes' in request.POST:
        language = request.POST.get('language')
        selected_items = request.POST.getlist('selected_items')
        item_names = selected_items if selected_items else [item.name for item in items]
        prompt = (
            f"Suggest 3 recipes using these ingredients: {', '.join(item_names)}. "
            "Other ingredients can be added as needed. "
            "Respond in JSON format as a list of objects with 'title' and 'details' fields. "
            "Example: [{\"title\": \"Recipe 1\", \"details\": \"Instructions here.\"}, ...]"
        )
        if language == 'ja':
            prompt += " Respond in Japanese."
        client = openai.OpenAI(api_key=api_key)
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                recipes = json.loads(match.group(0))
        except openai.RateLimitError:
            messages.error(request, "OpenAI quota exceeded. Please check your API key's usage and billing.")
        except AuthenticationError:
            messages.error(request, "Invalid OpenAI API key. Please check your API key and try again.")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")
    return render(request, 'refrigerator/index.html', {'items': items, 'recipes': recipes})


def signup(request):
    """
    User registration view. Handles new user creation and validation.
    """
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


def login_view(request):
    """
    Login view. Supports optional temporary OpenAI API key for the session.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        temp_api_key = request.POST.get('temp_api_key', '').strip()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if temp_api_key:
                request.session['temp_openai_api_key'] = temp_api_key
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'refrigerator/login.html')


def logout_view(request):
    """
    Logout view. Removes temporary API key from session.
    """
    logout(request)
    if 'temp_openai_api_key' in request.session:
        del request.session['temp_openai_api_key']
    return redirect('login')


@login_required
def add_item(request):
    """
    Add a new item to the user's fridge.
    """
    if request.method == 'POST':
        item_name = request.POST.get('item_name')
        item_quantity = request.POST.get('item_quantity')
        how_to_count = request.POST.get('how_to_count')
        current_date = datetime.datetime.now().date()
        if item_name and item_quantity and how_to_count is not None:
            user = User.objects.get(username=request.user.username)
            if Item.objects.filter(user=user, name=item_name).exists():
                messages.error(request, "Item already exists")
            else:
                item = Item(user=user, name=item_name, quantity=item_quantity, how_to_count=how_to_count, added_on=current_date)
                item.save()
                messages.success(request, "Item added successfully")
        return redirect('index')
    return redirect('index')


@login_required
def delete_item(request):
    """
    Delete an item from the user's fridge.
    """
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        try:
            item = Item.objects.get(id=item_id)
            item.delete()
        except Item.DoesNotExist:
            pass
    return redirect('index')


@login_required
def clear_all_items(request):
    """
    Remove all items from the fridge.
    """
    if request.method == 'POST':
        Item.objects.all().delete()
    return redirect('index')


@login_required
def update_item_quantity(request):
    """
    Update the quantity and fraction of a fridge item.
    """
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        new_quantity = request.POST.get('new_quantity')
        new_fraction = request.POST.get('new_fraction')
        try:
            item = Item.objects.get(id=item_id)
            item.quantity = new_quantity
            item.quantity_fraction = new_fraction
            item.quantity_if_zero = (new_quantity == '0')
            item.save()
        except Item.DoesNotExist:
            pass
    return redirect('index')


@login_required
def save_recipe(request):
    """
    Save a recipe to the user's saved recipes.
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        details = request.POST.get('details')
        user = request.user
        Recipes.objects.create(user=user, title=title, instructions=details)
        messages.success(request, 'Recipe saved!')
    return redirect('index')