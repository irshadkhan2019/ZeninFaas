from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Function(models.Model):
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
    
    ]
    name = models.CharField(max_length=100,unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    language = models.CharField(max_length=50,choices=LANGUAGE_CHOICES)
    memory_limit = models.IntegerField(default=128)  
    cpu_limit = models.IntegerField(default=5000)        
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name 
