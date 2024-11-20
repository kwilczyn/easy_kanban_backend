from django.urls import path
from .views import BoardListCreate, BoardRetrieveUpdateDestroy, ListListCreate, ListRetrieveUpdateDestroy, TaskListCreate, TaskRetrieveUpdateDestroy, get_csrf_token, ListForward, ListBackward, create_test_data, RegisterView, remove_test_users    
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('csrf-token/', get_csrf_token, name='get-csrf-token'),

    path('board/', BoardListCreate.as_view(), name='board-list-create'),
    path('board/<int:board_pk>/', BoardRetrieveUpdateDestroy.as_view(), name='board-detail'),
    
    path('board/<int:board_pk>/list/', ListListCreate.as_view(), name='list-list-create'),
    path('board/<int:board_pk>/list/<int:list_pk>/', ListRetrieveUpdateDestroy.as_view(), name='list-detail'),
    path('board/<int:board_pk>/list/<int:list_pk>/forward/', ListForward.as_view(), name='list-forward'),
    path('board/<int:board_pk>/list/<int:list_pk>/backward/', ListBackward.as_view(), name='list-backward'),
    
    path('board/<int:board_pk>/list/<int:list_pk>/task/', TaskListCreate.as_view(), name='task-list-create'),
    path('board/<int:board_pk>/list/<int:list_pk>/task/<int:task_pk>/', TaskRetrieveUpdateDestroy.as_view(), name='task-detail'),

    path('create_test_data/', create_test_data, name='create-test-data'),
    path('remove_test_users/', remove_test_users, name='remove-test-users'),
]

