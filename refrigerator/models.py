from django.db import models
from django.contrib.auth.models import User

# Item model: fridge items for each user
class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')  # Linked to each user
    name = models.CharField(max_length=50)  # Item name
    quantity = models.PositiveIntegerField()  # Quantity
    quantity_fraction = models.CharField(max_length=10, blank=True, default='')  # Fractional quantity (optional)
    quantity_if_zero = models.BooleanField(default=False)  # If quantity is zero
    how_to_count = models.IntegerField(choices=[(0, 'pcs'), (1, 'ml'), (2, 'g'), (3, 'pack(s)')], default=0)  # Unit of measurement
    added_on = models.DateField()  # Date added

    def __str__(self):
        return f"{self.name} (x{self.quantity}), added on {self.added_on})"

#--- Recipe model ---
class Recipes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    title = models.CharField(max_length=100)
    instructions = models.TextField()

    def __str__(self):
        return self.title