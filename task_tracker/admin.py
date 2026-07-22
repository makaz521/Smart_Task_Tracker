from django.contrib import admin

# Register your models here.
from .models import UserProfile  # Import UserProfile model

# Register UserProfile so it appears in Django Admin
admin.site.register(UserProfile)