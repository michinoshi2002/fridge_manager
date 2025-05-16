from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),  # Login
    path('logout/', views.logout_view, name='logout'),  # Logout
    path('signup/', views.signup, name='signup'),  # Sign up
    path('index/', views.index, name='index'),  # Main page
    path('add_item/', views.add_item, name='add_item'),  # Add item
    path('delete_item/', views.delete_item, name='delete_item'),  # Delete item
    path('update_item_quantity/', views.update_item_quantity, name='update_item_quantity'),  # Update quantity
    path('clear_all_items/', views.clear_all_items, name='clear_all_items'),  # Clear all items
]