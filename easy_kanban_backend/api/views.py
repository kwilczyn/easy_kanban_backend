from django.shortcuts import get_object_or_404
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from .models import Board, List, Task
from .serializers import BoardBasicSerializer, BoardSerializer, ListSerializer, TaskSerializer, TaskPatchSerializer
from django.http import JsonResponse
from django.middleware.csrf import get_token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.db import transaction


class BoardListCreate(generics.ListCreateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardBasicSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['users__id', 'title']

class BoardRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    lookup_field = 'pk'
    lookup_url_kwarg = 'board_pk'


# List Views
class ListListCreate(generics.ListCreateAPIView):
    serializer_class = ListSerializer

    def get_queryset(self):
        board_pk = self.kwargs['board_pk']
        return List.objects.filter(board_id=board_pk)

    def perform_create(self, serializer):
        board_pk = self.kwargs['board_pk']
        board = get_object_or_404(Board, pk=board_pk)
        serializer.save(board=board, position=board.get_next_position())

class ListRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ListSerializer
    lookup_field = 'pk'
    lookup_url_kwarg = 'list_pk'

    def get_queryset(self):
        board_pk = self.kwargs['board_pk']
        return List.objects.filter(board_id=board_pk)


class ListForwardBackward(generics.UpdateAPIView):
    serializer_class = ListSerializer
    lookup_field = 'pk'
    lookup_url_kwarg = 'list_pk'

    def get_queryset(self):
        board_pk = self.kwargs['board_pk']
        return List.objects.filter(board_id=board_pk)

class ListForward(ListForwardBackward):

    def perform_update(self, serializer):
        with transaction.atomic():
            targetList = serializer.instance
            if targetList.position < (targetList.board.get_next_position()-1):
                serializer.validated_data['position'] = targetList.position + 1
                other_list = targetList.board.lists.exclude(pk=targetList.pk).filter(position=targetList.position + 1).first()
                if other_list:
                    other_list.position -= 1
                    other_list.save()
            serializer.save()

class ListBackward(ListForwardBackward):
    
    def perform_update(self, serializer):
        with transaction.atomic():
            targetList = serializer.instance
            if targetList.position > 0:
                serializer.validated_data['position'] = targetList.position - 1
                other_list = targetList.board.lists.exclude(pk=targetList.pk).filter(position=targetList.position - 1).first()
                if other_list:
                    other_list.position += 1
                    other_list.save()
            serializer.save()


# Task Views
class TaskListCreate(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        board_pk = self.kwargs['board_pk']
        list_pk = self.kwargs['list_pk']
        return Task.objects.filter(list_id=list_pk, list__board_id=board_pk)

    def perform_create(self, serializer):
        board_pk = self.kwargs['board_pk']
        list_pk = self.kwargs['list_pk']
        task_list = get_object_or_404(List, pk=list_pk, board_id=board_pk)
        serializer.save(list=task_list, position=task_list.get_next_position())

class TaskRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskPatchSerializer
    lookup_field = 'pk'
    lookup_url_kwarg = 'task_pk'

    def get_queryset(self):
        board_pk = self.kwargs['board_pk']
        list_pk = self.kwargs['list_pk']
        return Task.objects.filter(list_id=list_pk, list__board_id=board_pk)
    
    def perform_update(self, serializer):
        targetList = serializer.validated_data.get('list')
        if targetList and (serializer.validated_data.get('position') is None):
            serializer.validated_data['position'] = targetList.get_next_position()
            serializer.save()
        elif serializer.validated_data.get('position') is not None:
            serializer.save()
            targetList = serializer.instance.list if targetList is None else targetList
            otherTasks = targetList.tasks.exclude(pk=serializer.instance.pk)
            for task in otherTasks:
                if task.position >= serializer.validated_data.get('position'):
                    task.position += 1
                    task.save()
        else:
            serializer.save()


@api_view(['GET'])
@permission_classes([AllowAny])
def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})


@api_view(['POST'])
@permission_classes([AllowAny])
def create_test_data(request):
    testUser = request.data.get('boards')[0].get('users')[0]
    Board.objects.filter(users__id=testUser).delete()

    for board in request.data.get('boards'):
        board_instance = Board.objects.create(title=board.get('title'))
        board_instance.users.add(testUser)
        for list in board.get('lists'):
            list_instance = List.objects.create(title=list.get('title'), board=board_instance, position=list.get('position'))
            for task in list.get('tasks'):
                Task.objects.create(title=task.get('title'), description=task.get('description'), list=list_instance, position=task.get('position'))

    return JsonResponse({'message': 'Test data created successfully'})