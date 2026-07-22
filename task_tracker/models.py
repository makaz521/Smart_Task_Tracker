from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# User Profile with role specification and phone number
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=50, 
        choices=[('Manager', 'Manager'), ('Team Member', 'Team Member')]
    )
    phone_number = models.CharField(max_length=15, null=True, blank=True)  # Phone number field

    def __str__(self):
        return f"{self.user.username} - {self.role}"

# Task model with additional fields
class Task(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]
    
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE)
    deadline = models.DateTimeField()  # ✅ Updated to store both date and time
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def progress(self):
        """Calculate task progress based on status."""
        progress_map = {
            "Pending": 0,
            "In Progress": 50,
            "Completed": 100
        }
        return progress_map.get(self.status, 0)
    
    def __str__(self):
        return self.name

# Notification model
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)  # New task field
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:30]}..."

