from django.contrib import admin
from .models import Trigger
# Register your models here.

class TriggerAdmin(admin.ModelAdmin):
    list_display=("name","function")
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

# showing interface to admin users
admin.site.register(Trigger, TriggerAdmin)    