from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Item, Recipes
import datetime
import json
import os
from google import genai
from google.genai import types

# Gemini Model Configuration
GEMINI_MODEL_NAME = "gemini-2.5-flash-preview-04-17"

def clean_unicode_escapes(text):
    """
    Replace unicode escape sequences in the text with actual characters.
    """
    if not text:
        return text
    return (
        text.replace('\\u000A', '\n')
            .replace('\\u002D', '-')
            .replace('\\u002E', '.')
            .replace('\\u002C', ',')
            .replace('\\u003A', ':')
    )

# Helper function to fetch recipes from Gemini API
def _fetch_recipes_from_gemini(api_key: str, item_names: list[str], language: str):
    """
    Fetches recipe suggestions from the Gemini API.
    Returns parsed JSON (list of dicts).
    Can raise exceptions from the Gemini API or json.JSONDecodeError.
    """
    prompt = (
        f"Suggest 3 recipes using these ingredients: {', '.join(item_names)}. "
        "Include the list of ingridients and amounts needed for each recipe. "
        "Other ingredients can be added as needed. "
        "Respond in JSON format as a list of objects with 'title' and 'details' fields. "
        "Example: [{\"title\": \"Recipe 1\", \"details\": \"Instructions here.\"}, ...]"
    )
    if language == 'ja':
        prompt += " Respond in Japanese."
    elif language == 'en':
        prompt += " Respond in English."

    client = genai.Client(api_key=api_key)
    contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
    generate_content_config = types.GenerateContentConfig(response_mime_type="application/json")
    
    all_contents = []
    for chunk in client.models.generate_content_stream(
        model=GEMINI_MODEL_NAME,
        contents=contents,
        config=generate_content_config
    ):
        if chunk and getattr(chunk, 'candidates', None):
            parts = chunk.candidates[0].content.parts
            if parts and hasattr(parts[0], 'text'):
                content = parts[0].text.strip()
                all_contents.append(content)
    
    full_content = "".join(all_contents)

    # Attempt to parse JSON, will raise json.JSONDecodeError if parsing fails
    return json.loads(full_content)

@login_required
def index(request):
    """
    Main page: Shows fridge items and handles recipe suggestions via Gemini API.
    """
    items = Item.objects.filter(user=request.user)
    recipes = [] # Initialize recipes list for suggested recipes
    # Use temporary API key from session if present, else use environment/global key
    api_key = request.session.get('temp_gemini_api_key') or os.environ.get('GEMINI_API_KEY')
    
    if request.method == 'POST' and 'suggest_recipes' in request.POST:
        if not api_key:
            messages.error(request, "Please set your Gemini API key to use recipe suggestions.")
        else:
            language = request.POST.get('language')
            selected_items_names = request.POST.getlist('selected_items')
            item_names_for_prompt = selected_items_names if selected_items_names else [item.name for item in items]
            
            try:
                # api_response is now expected to be parsed JSON (list of dicts)
                # or an exception will be raised by _fetch_recipes_from_gemini
                recipes = _fetch_recipes_from_gemini(api_key, item_names_for_prompt, language)

            except types.BlockedPromptException as e:
                messages.error(request, f"Recipe suggestion blocked by content policy: {e}")
            except types.StopCandidateException as e: 
                messages.error(request, f"Recipe suggestion stopped prematurely: {e}")
            except json.JSONDecodeError as e: # Specifically catch JSON decoding errors
                messages.error(request, f"Failed to parse recipe suggestions from the API: {e}")
            except Exception as e: # Fallback for any other unexpected errors
                messages.error(request, f"An unexpected error occurred while fetching recipes: {e}")
                
    saved_recipes = request.user.recipes.all()
    for recipe in saved_recipes:
        if recipe.instructions:
            recipe.instructions = clean_unicode_escapes(recipe.instructions)
    return render(request, 'refrigerator/index.html', {'items': items, 'recipes': recipes, 'saved_recipes': saved_recipes})

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
    Login view. Supports optional temporary Gemini API key for the session.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        temp_api_key = request.POST.get('temp_api_key', '').strip()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if temp_api_key:
                request.session['temp_gemini_api_key'] = temp_api_key
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'refrigerator/login.html')


def logout_view(request):
    """
    Logout view. Removes temporary API key from session.
    """
    logout(request)
    if 'temp_gemini_api_key' in request.session:
        del request.session['temp_gemini_api_key']
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
            user = request.user
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
    Remove all items from the current user's fridge.
    """
    if request.method == 'POST':
        Item.objects.filter(user=request.user).delete()
        messages.success(request, "All your items have been cleared.")
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
    Save selected recipes to the user's saved recipes (batch save).
    """
    if request.method == 'POST':
        titles = request.POST.getlist('recipe_title')
        details_list = request.POST.getlist('recipe_details')
        user = request.user
        saved_count = 0
        for title, details in zip(titles, details_list):
            cleaned_details = clean_unicode_escapes(details) # Clean details before saving
            # Prevent duplicate saves for the same user/title
            if not Recipes.objects.filter(user=user, title=title).exists():
                Recipes.objects.create(user=user, title=title, instructions=cleaned_details)
                saved_count += 1
        if saved_count:
            messages.success(request, f"{saved_count} recipe(s) saved!")
        else:
            messages.info(request, "No new recipes were saved.")
    return redirect('index')

@login_required
def delete_saved_recipe(request):
    """
    Delete a saved recipe for the current user by recipe ID.
    """
    if request.method == 'POST':
        recipe_id = request.POST.get('recipe_id')
        try:
            recipe = Recipes.objects.get(id=recipe_id, user=request.user)
            recipe.delete()
            messages.success(request, "Recipe deleted successfully.")
        except Recipes.DoesNotExist:
            messages.error(request, "Recipe not found or you do not have permission to delete it.")
    return redirect('index')