from django.contrib import admin
from .models import User, Board, List, Task

# Register your models here.

admin.site.register(Board)
admin.site.register(List)
admin.site.register(Task)
