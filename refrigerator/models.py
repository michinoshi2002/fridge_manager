from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username
    
class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items', null=True)
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    date_of_purchase = models.DateField()

    def __str__(self):
        return f"{self.name} (x{self.quantity})"

#Later.

# class Recipes(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
#     title = models.CharField(max_length=200)
#     ingredients = models.TextField()
#     instructions = models.TextField()

#     def __str__(self):
#         return self.title