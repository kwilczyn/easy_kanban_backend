from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from api.models import Board, List, Task
from api.serializers import BoardBasicSerializer, BoardSerializer, ListSerializer, TaskSerializer, TaskPatchSerializer


class GetCSRFTokenTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('get-csrf-token')

    def test_get_csrf_token(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('csrfToken', response.json())


class BoardListCreateTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('board-list-create')
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.board_data = {'title': 'Test Board', 'users': [self.user.pk]}

    def test_create_board(self):
        response = self.client.post(self.url, self.board_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Board.objects.count(), 1)
        self.assertEqual(Board.objects.get().title, 'Test Board')

    def test_create_board_without_title(self):
        response = self.client.post(self.url, {'users': [self.user.pk]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Board.objects.count(), 0)

    def test_create_board_without_users(self):
        response = self.client.post(self.url, {'title': 'Test Board'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Board.objects.count(), 0)

    def test_create_board_with_invalid_user(self):
        response = self.client.post(self.url, {'title': 'Test Board', 'users': [9999]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Board.objects.count(), 0)

    def test_create_board_with_multiple_users(self):
        user2 = User.objects.create_user(username='testuser2', password='testpassword')
        response = self.client.post(self.url, {'title': 'Test Board', 'users': [self.user.pk, user2.pk]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Board.objects.get().users.count(), 2)

    def test_create_board_with_duplicate_users(self):
        response = self.client.post(self.url, {'title': 'Test Board', 'users': [self.user.pk, self.user.pk]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Board.objects.get().users.count(), 1)

    def test_create_board_with_too_long_title(self):
        long_title = 'x' * 101
        response = self.client.post(self.url, {'title': long_title, 'users': [self.user.pk]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Board.objects.count(), 0)

    def test_create_board_with_max_length_title(self):
        max_length_title = 'x' * 100
        response = self.client.post(self.url, {'title': max_length_title, 'users': [self.user.pk]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Board.objects.count(), 1)

    def test_list_boards(self):
        Board.objects.create(title='Board 1')
        Board.objects.create(title='Board 2')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_boards_by_user(self):
        another_user = User.objects.create_user(username='anotheruser', password='anotherpassword') 
        board1 = Board.objects.create(title='Board 1')
        board2 = Board.objects.create(title='Board 2')
        board1.users.add(self.user)
        board2.users.add(another_user)
        response = self.client.get(self.url, {'users__id': self.user.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Board 1')

    def test_filter_boards_by_title(self):
        Board.objects.create(title='Board 1')
        Board.objects.create(title='Board 2')
        response = self.client.get(self.url, {'title': 'Board 1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Board 1')

    def test_filter_boards_by_user_and_title(self):
        board1 = Board.objects.create(title='Board 1')
        board2 = Board.objects.create(title='Board 2')
        board1.users.add(self.user)
        board2.users.add(self.user)
        response = self.client.get(self.url, {'users__id': self.user.pk, 'title': 'Board 1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Board 1')

class BoardRetrieveUpdateDestroyTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.board = Board.objects.create(title='Test Board')
        self.board.users.add(self.user)
        self.url = reverse('board-detail', kwargs={'board_pk': self.board.pk})
        self.board_data = {'title': 'Updated Board', 'users': [self.user.pk]}

    def test_retrieve_board(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Board')

    def test_retrieve_board_not_found(self):
        response = self.client.get(reverse('board-detail', kwargs={'board_pk': 9999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_board(self):
        response = self.client.put(self.url, self.board_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Board.objects.get().title, 'Updated Board')

    def test_update_board_not_found(self):
        response = self.client.put(reverse('board-detail', kwargs={'board_pk': 9999}), self.board_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_board_with_invalid_user(self):
        response = self.client.put(self.url, {'title': 'Updated Board', 'users': [9999]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Board.objects.get().title, 'Test Board')

    def test_update_board_with_too_long_title(self):    
        long_title = 'x' * 101
        response = self.client.put(self.url, {'title': long_title, 'users': [self.user.pk]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Board.objects.get().title, 'Test Board')

    def test_update_board_with_max_length_title(self):
        max_length_title = 'x' * 100
        response = self.client.put(self.url, {'title': max_length_title, 'users': [self.user.pk]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Board.objects.get().title, max_length_title)

    def test_update_board_without_title(self):
        response = self.client.put(self.url, {'users': [self.user.pk]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Board.objects.get().title, 'Test Board')

    def test_update_board_without_users(self):
        response = self.client.put(self.url, {'title': 'Updated Board'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Board.objects.get().title, 'Test Board')

    def test_delete_board(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Board.objects.count(), 0)

    def test_delete_board_not_found(self):
        response = self.client.delete(reverse('board-detail', kwargs={'board_pk': 9999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_board_that_includes_lists(self):
        List.objects.create(title='Test List', board=self.board)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Board.objects.count(), 0)
        self.assertEqual(List.objects.count(), 0)

    def test_patch_board_title(self):
        response = self.client.patch(self.url, {'title': 'Patched Board'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Board.objects.get().title, 'Patched Board')

    def test_patch_board_users(self):
        user2 = User.objects.create_user(username='testuser2', password='testpassword')
        response = self.client.patch(self.url, {'users': [user2.pk]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Board.objects.get().users.count(), 1)
        self.assertEqual(Board.objects.get().users.first(), user2)


class ListListCreateTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.board = Board.objects.create(title='Test Board')
        self.board.users.add(self.user)
        self.url = reverse('list-list-create', kwargs={'board_pk': self.board.pk})
        self.list_data = {'title': 'Test List'}

    def test_create_list(self):
        response = self.client.post(self.url, self.list_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(List.objects.count(), 1)
        self.assertEqual(List.objects.get().title, 'Test List')

    def test_create_list_without_title(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(List.objects.count(), 0)

    def test_create_list_with_too_long_title(self):
        long_title = 'x' * 101
        response = self.client.post(self.url, {'title': long_title}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(List.objects.count(), 0)

    def test_create_list_with_max_length_title(self):
        max_length_title = 'x' * 100
        response = self.client.post(self.url, {'title': max_length_title}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(List.objects.count(), 1)

    def test_create_list_invalid_board_pk(self):
        response = self.client.post(reverse('list-list-create', kwargs={'board_pk': 9999}), self.list_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(List.objects.count(), 0)

    def test_list_lists(self):
        List.objects.create(title='List 1', board=self.board)
        List.objects.create(title='List 2', board=self.board)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_lists_by_board(self):
        board2 = Board.objects.create(title='Test Board 2')
        List.objects.create(title='List 1', board=self.board)
        List.objects.create(title='List 2', board=board2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'List 1')

class ListRetrieveUpdateDestroyTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.board = Board.objects.create(title='Test Board')
        self.board.users.add(self.user)
        self.list = List.objects.create(title='Test List', board=self.board)
        self.url = reverse('list-detail', kwargs={'board_pk': self.board.pk, 'list_pk': self.list.pk})
        self.list_data = {'title': 'Updated List'}

    def test_retrieve_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test List')

    def test_retrieve_list_not_found(self):
        response = self.client.get(reverse('list-detail', kwargs={'board_pk': self.board.pk, 'list_pk': 9999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_list_invalid_board_pk(self):
        response = self.client.get(reverse('list-detail', kwargs={'board_pk': 9999, 'list_pk': self.list.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_list(self):
        response = self.client.put(self.url, self.list_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(List.objects.get().title, 'Updated List')

    def test_update_list_not_found(self):
        response = self.client.put(reverse('list-detail', kwargs={'board_pk': self.board.pk, 'list_pk': 9999}), self.list_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_list_with_too_long_title(self):
        long_title = 'x' * 101
        response = self.client.put(self.url, {'title': long_title}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(List.objects.get().title, 'Test List')

    def test_update_list_with_max_length_title(self):
        max_length_title = 'x' * 100
        response = self.client.put(self.url, {'title': max_length_title}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(List.objects.get().title, max_length_title)

    def test_update_list_without_title(self):
        response = self.client.put(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(List.objects.get().title, 'Test List')

    def test_delete_list(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(List.objects.count(), 0)

    def test_delete_list_not_found(self):
        response = self.client.delete(reverse('list-detail', kwargs={'board_pk': self.board.pk, 'list_pk': 9999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_list_that_includes_tasks(self):
        Task.objects.create(title='Test Task', list=self.list)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Task.objects.count(), 0)

    def test_delete_list_wrong_board_pk(self):
        response = self.client.delete(reverse('list-detail', kwargs={'board_pk': 9999, 'list_pk': self.list.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_list_title(self):
        response = self.client.patch(self.url, {'title': 'Patched List'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(List.objects.get().title, 'Patched List')


class ListForwardBackwardTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.board = Board.objects.create(title='Test Board')
        self.board.users.add(self.user)
        self.list1 = List.objects.create(title='Test List 1', board=self.board, position=0)
        self.list2 = List.objects.create(title='Test List 2', board=self.board, position=1)
        self.list3 = List.objects.create(title='Test List 3', board=self.board, position=2)
        

class ListForward(ListForwardBackwardTestCase):
    
    def test_move_list_position_forward(self):
        url = reverse('list-forward', kwargs={'board_pk': self.board.pk, 'list_pk': self.list1.pk})
        response = self.client.patch(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(List.objects.get(pk=self.list1.pk).position, 1)
        self.assertEqual(List.objects.get(pk=self.list2.pk).position, 0)
        self.assertEqual(List.objects.get(pk=self.list3.pk).position, 2)

class ListBackward(ListForwardBackwardTestCase):
    
    def test_move_list_position_backward(self):
        url = reverse('list-backward', kwargs={'board_pk': self.board.pk, 'list_pk': self.list2.pk})
        response = self.client.patch(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(List.objects.get(pk=self.list1.pk).position, 1)
        self.assertEqual(List.objects.get(pk=self.list2.pk).position, 0)
        self.assertEqual(List.objects.get(pk=self.list3.pk).position, 2)


class TaskListCreateTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.board = Board.objects.create(title='Test Board')
        self.board.users.add(self.user)
        self.list = List.objects.create(title='Test List', board=self.board)
        self.url = reverse('task-list-create', kwargs={'board_pk': self.board.pk, 'list_pk': self.list.pk})
        self.task_data = {'title': 'Test Task'}

    def test_create_task(self):
        response = self.client.post(self.url, self.task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.get().title, 'Test Task')

    def test_create_task_including_description(self):
        response = self.client.post(self.url, {'title': 'Test Task', 'description': 'Test Description'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.get().description, 'Test Description')

    def test_create_task_without_title(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Task.objects.count(), 0)

    def test_create_task_with_too_long_title(self):
        long_title = 'x' * 101
        response = self.client.post(self.url, {'title': long_title}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Task.objects.count(), 0)

    def test_create_task_with_max_length_title(self):
        max_length_title = 'x' * 100
        response = self.client.post(self.url, {'title': max_length_title}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)

    def test_create_task_invalid_list_pk(self):
        response = self.client.post(reverse('task-list-create', kwargs={'board_pk': self.board.pk, 'list_pk': 9999}), self.task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Task.objects.count(), 0)

    def test_create_task_invalid_board_pk(self):
        response = self.client.post(reverse('task-list-create', kwargs={'board_pk': 9999, 'list_pk': self.list.pk}), self.task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Task.objects.count(), 0)

    def test_list_tasks(self):
        Task.objects.create(title='Task 1', list=self.list)
        Task.objects.create(title='Task 2', list=self.list)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_tasks_by_list(self):
        list2 = List.objects.create(title='Test List 2', board=self.board)
        Task.objects.create(title='Task 1', list=self.list)
        Task.objects.create(title='Task 2', list=list2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Task 1')

    def test_filter_tasks_by_board(self):
        board2 = Board.objects.create(title='Test Board 2')
        list2 = List.objects.create(title='Test List 2', board=board2)
        Task.objects.create(title='Task 1', list=self.list)
        Task.objects.create(title='Task 2', list=list2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Task 1')

class TaskRetrieveUpdateDestroyTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.board = Board.objects.create(title='Test Board')
        self.board.users.add(self.user)
        self.list = List.objects.create(title='Test List', board=self.board)
        self.task = Task.objects.create(title='Test Task', description='My example desc', list=self.list)
        self.url = reverse('task-detail', kwargs={'board_pk': self.board.pk, 'list_pk': self.list.pk, 'task_pk': self.task.pk})
        self.task_data = {'title': 'Updated Task', 'description': 'Updated desc', 'position': 1, 'list': self.list.pk}

    def test_retrieve_task(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Task')
        self.assertEqual(response.data['description'], 'My example desc')
        self.assertEqual(response.data['position'], 0)

    def test_retrieve_task_not_found(self):
        response = self.client.get(reverse('task-detail', kwargs={'board_pk': self.board.pk, 'list_pk': self.list.pk, 'task_pk': 9999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_task_invalid_list_pk(self):
        response = self.client.get(reverse('task-detail', kwargs={'board_pk': self.board.pk, 'list_pk': 9999, 'task_pk': self.task.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_task_invalid_board_pk(self):
        response = self.client.get(reverse('task-detail', kwargs={'board_pk': 9999, 'list_pk': self.list.pk, 'task_pk': self.task.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_task(self):
        response = self.client.put(self.url, self.task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.get().title, 'Updated Task')

    def test_update_task_not_found(self):
        response = self.client.put(reverse('task-detail', kwargs={'board_pk': self.board.pk, 'list_pk': self.list.pk, 'task_pk': 9999}), self.task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_task_with_too_long_title(self):
        long_title = 'x' * 101
        invalid_data = self.task_data
        invalid_data['title'] = long_title
        response = self.client.put(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Task.objects.get().title, 'Test Task')

    def test_update_task_with_max_length_title(self):
        max_length_title = 'x' * 100
        valid_data = self.task_data
        valid_data['title'] = max_length_title
        response = self.client.put(self.url, valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.get().title, max_length_title)

    def test_update_task_without_title(self):
        invalid_data = self.task_data
        invalid_data.pop('title')
        response = self.client.put(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Task.objects.get().title, 'Test Task')

    def test_update_task_without_list(self):
        invalid_data = self.task_data
        invalid_data.pop('list')
        response = self.client.put(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Task.objects.get().list, self.list)

    def test_update_task_with_invalid_list(self):
        invalid_data = self.task_data
        invalid_data['list'] = 9999
        response = self.client.put(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Task.objects.get().list, self.list)

    def test_update_task_with_list_without_position(self):
        updated_data = self.task_data
        updated_data.pop('position')
        task2 = Task.objects.create(title='Task 2', list=self.list, position=5)
        response = self.client.put(self.url, updated_data, format='json')
        # position should be set to the next available position in the targeted list
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.get(pk=self.task.id).position, 6)

    def test_update_task_with_list_without_position_does_not_move_positions_of_bottom_tasks(self):
        task0= Task.objects.create(title='Task 0', list=self.list, position=0)
        task2 = Task.objects.create(title='Task 2', list=self.list, position=5)
        updated_data = self.task_data
        updated_data.pop('position')
        response = self.client.put(self.url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.get(pk=self.task.id).position, 6)
        self.assertEqual(Task.objects.get(pk=task2.id).position, 5)
        self.assertEqual(Task.objects.get(pk=task0.id).position, 0)


    def test_update_task_with_list_and_position_moves_positions_of_bottom_tasks(self):
        task0= Task.objects.create(title='Task 1', list=self.list, position=0)
        task2 = Task.objects.create(title='Task 2', list=self.list, position=5)
        task3 = Task.objects.create(title='Task 3', list=self.list, position=10)
        updated_data = self.task_data
        updated_data['position'] = 5
        response = self.client.put(self.url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.get(pk=self.task.id).position, 5)
        self.assertEqual(Task.objects.get(pk=task2.id).position, 6)
        self.assertEqual(Task.objects.get(pk=task3.id).position, 11)
        self.assertEqual(Task.objects.get(pk=task0.id).position, 0)

    def test_update_task_with_another_list_and_position_moves_positions_of_bottom_tasks(self):
        list2 = List.objects.create(title='Test List 2', board=self.board)
        task0= Task.objects.create(title='Task 1', list=list2, position=0)
        task2 = Task.objects.create(title='Task 2', list=list2 , position=5)
        task3 = Task.objects.create(title='Task 3', list=list2, position=10)
        updated_data = self.task_data
        updated_data['list'] = list2.pk
        updated_data['position'] = 5
        response = self.client.put(self.url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.get(pk=self.task.id).position, 5)
        self.assertEqual(Task.objects.get(pk=task2.id).position, 6)
        self.assertEqual(Task.objects.get(pk=task3.id).position, 11)
        self.assertEqual(Task.objects.get(pk=task0.id).position, 0)
        

    def test_delete_task(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)

    def test_delete_task_not_found(self):
        response = self.client.delete(reverse('task-detail', kwargs={'board_pk': self.board.pk, 'list_pk': self.list.pk, 'task_pk': 9999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_task_wrong_list_pk(self):
        response = self.client.delete(reverse('task-detail', kwargs={'board_pk': self.board.pk, 'list_pk': 9999, 'task_pk': self.task.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_task_wrong_board_pk(self): 
        response = self.client.delete(reverse('task-detail', kwargs={'board_pk': 9999, 'list_pk': self.list.pk, 'task_pk': self.task.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_task_title(self):
        response = self.client.patch(self.url, {'title': 'Patched Task'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.get().title, 'Patched Task')

    def test_patch_task_description(self):
        response = self.client.patch(self.url, {'description': 'Patched desc'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.get().description, 'Patched desc')

    def test_patch_task_position(self):
        response = self.client.patch(self.url, {'position': 5}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.get().position, 5)

    def test_patch_task_list(self):
        list2 = List.objects.create(title='Test List 2', board=self.board)
        task2 = Task.objects.create(title='Test Task 2', list=list2, position=5)
        response = self.client.patch(self.url, {'list': list2.pk}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.get(pk=self.task.id).list, list2)
        self.assertEqual(Task.objects.get(pk=self.task.id).position, 6)


  


