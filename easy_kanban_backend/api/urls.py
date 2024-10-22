from django.urls import path
from .views import BoardListCreate, BoardRetrieveUpdateDestroy, ListListCreate, ListRetrieveUpdateDestroy, TaskListCreate, TaskRetrieveUpdateDestroy, get_csrf_token, ListForward, ListBackward    


urlpatterns = [
    path('csrf-token/', get_csrf_token, name='get-csrf-token'),

    path('board/', BoardListCreate.as_view(), name='board-list-create'),
    path('board/<int:board_pk>/', BoardRetrieveUpdateDestroy.as_view(), name='board-detail'),
    
    path('board/<int:board_pk>/list/', ListListCreate.as_view(), name='list-list-create'),
    path('board/<int:board_pk>/list/<int:list_pk>/', ListRetrieveUpdateDestroy.as_view(), name='list-detail'),
    path('board/<int:board_pk>/list/<int:list_pk>/forward/', ListForward.as_view(), name='list-forward'),
    path('board/<int:board_pk>/list/<int:list_pk>/backward/', ListBackward.as_view(), name='list-backward'),
    
    path('board/<int:board_pk>/list/<int:list_pk>/task/', TaskListCreate.as_view(), name='task-list-create'),
    path('board/<int:board_pk>/list/<int:list_pk>/task/<int:task_pk>/', TaskRetrieveUpdateDestroy.as_view(), name='task-detail'),
]

