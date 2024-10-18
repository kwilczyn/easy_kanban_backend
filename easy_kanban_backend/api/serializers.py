from rest_framework import serializers
from django.contrib.auth.models import User
from api.models import Board, Task, List

class TaskSerializer(serializers.ModelSerializer):  
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'position']

class TaskPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'position', 'list']


class ListSerializer(serializers.ModelSerializer):
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = List
        fields = ['id', 'title', 'tasks']

    def get_tasks(self, obj):
        tasks = obj.tasks.all().order_by('position')
        return TaskSerializer(tasks, many=True).data


class BoardBasicSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(
    queryset=User.objects.all(),
    many=True,
    )
    class Meta:
        model = Board
        fields = ['id', 'title', 'users']


class BoardSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(
    queryset=User.objects.all(),
    many=True
    )
    lists = ListSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = '__all__'

    def create(self, validated_data):
        users = validated_data.pop('users')
        board = Board.objects.create(**validated_data)
        board.users.set(users)
        return board