from django.contrib import admin
from .models import User, Board, List, Task

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'email')
    class Meta:
        model = User
        filter_horizontal = ('boards',)


class BoardAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'created_at', 'updated_at')
    list_filter = ['users']
    class Meta:
        model = Board
    

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Board, BoardAdmin)
admin.site.register(List)
admin.site.register(Task)
