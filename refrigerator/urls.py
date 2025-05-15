from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('index/', views.index, name='index'),
    path('add_item/', views.add_item, name='add_item'),
    path('delete_item/', views.delete_item, name='delete_item'),
    path('update_item_quantity/', views.update_item_quantity, name='update_item_quantity'),
    path('clear_all_items/', views.clear_all_items, name='clear_all_items'),
]