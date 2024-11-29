from django.contrib import admin

# Register your models here.

from .models import TestUser

admin.site.register(TestUser)