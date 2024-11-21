from rest_framework import serializers
from django.contrib.auth.models import User
from api.models import Board, Task, List
from django.contrib.auth.password_validation import validate_password

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
        fields = ['id', 'title', 'tasks', 'position']

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
    lists = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = '__all__'

    def create(self, validated_data):
        users = validated_data.pop('users')
        board = Board.objects.create(**validated_data)
        board.users.set(users)
        return board
    
    def get_lists(self, obj):
        lists = obj.lists.all().order_by('position')
        return ListSerializer(lists, many=True).data
    

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password_confirm', 'email', 'first_name', 'last_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords are not the same"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        #create Initial Boards and lists
        create_initial_board(user, "My Board")
        create_initial_board(user, "My Second Board")
        return user
    
def create_initial_board(user, title):
    initialBoard = Board.objects.create(title=title)
    initialBoard.users.set([user])
    List.objects.create(title="To Do", board=initialBoard)
    List.objects.create(title="In Progress", board=initialBoard)
    List.objects.create(title="Done", board=initialBoard)
    return initialBoard