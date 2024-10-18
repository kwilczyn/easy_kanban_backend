from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator


class Board(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    users = models.ManyToManyField(User)

    def __str__(self):
        return self.title
    
class List(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    board = models.ForeignKey(Board, related_name="lists", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"({self.board.title}) {self.title}"
    
    def get_next_position(self):
        if not self.tasks.exists():
            return 0
        else:
            return self.tasks.aggregate(models.Max('position'))['position__max'] + 1
    
class Task(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500, null=True, blank=True, validators=[MaxLengthValidator(500)])
    list = models.ForeignKey(List, related_name="tasks", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    position = models.IntegerField(default=0)

    def __str__(self):
        return self.title