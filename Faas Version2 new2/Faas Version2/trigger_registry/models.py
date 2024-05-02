from django.db import models
from function_registry.models import Function
from django.contrib.auth.models import User

# Create your models here.
class Trigger(models.Model):
    name = models.CharField(max_length=100)
    function = models.ForeignKey(Function, on_delete=models.CASCADE,)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def delete_with_function(self):
        self.function.delete()
        self.delete()

    def __str__(self):
        return self.name    