from django.db import models
from django.contrib.auth.models import User

class Menu(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menu_file = models.FileField(upload_to='menus/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_text = models.TextField(blank=True)

class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    recommendations = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)