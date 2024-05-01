from django.contrib import admin
from .models import Function
# Register your models here.

class FunctionAdmin(admin.ModelAdmin):
    list_display=("name","language","cpu_limit","memory_limit","user")
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

# showing interface to admin users
admin.site.register(Function, FunctionAdmin)    
