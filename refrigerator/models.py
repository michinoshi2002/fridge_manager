from django.db import models
from django.contrib.auth.models import User

# Item model: fridge items for each user
class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items', default=1)  # Linked to each user
    name = models.CharField(max_length=100)  # Item name
    quantity = models.PositiveIntegerField()  # Quantity
    added_on = models.DateField()  # Date added

    def __str__(self):
        return f"{self.name} (x{self.quantity}), added on {self.added_on})"

# --- Recipe model (will figure it out later) ---
# class Recipes(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
#     title = models.CharField(max_length=200)
#     ingredients = models.TextField()
#     instructions = models.TextField()
#
#     def __str__(self):
#         return self.title