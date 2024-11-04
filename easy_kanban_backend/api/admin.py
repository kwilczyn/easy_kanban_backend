from django.contrib import admin
from .models import User, Board, List, Task

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'email')
    class Meta:
        model = User
        filter_horizontal = ('boards',)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Board)
admin.site.register(List)
admin.site.register(Task)
