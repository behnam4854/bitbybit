from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Goal)
admin.site.register(TaskGroup)
admin.site.register(UserReminder)

