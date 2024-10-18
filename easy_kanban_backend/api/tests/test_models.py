from django.test import TestCase
from django.contrib.auth.models import User
from api.models import Board, List, Task
from django.core.exceptions import ValidationError


class BoardModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.board = Board.objects.create(title='Test Board')

    def test_board_creation(self):
        self.assertEqual(self.board.title, 'Test Board')
        self.assertEqual(self.board.users.count(), 0)

    def test_board_users(self):
        self.board.users.add(self.user)
        self.assertEqual(self.board.users.count(), 1)
        self.assertEqual(self.board.users.first(), self.user)

    def test_board_titile_is_required(self):
        board = Board()
        with self.assertRaises(ValidationError):
            board.full_clean()

    def test_board_title_over_max_length(self):
        long_title = 'x' * 101
        board = Board(title=long_title)
        with self.assertRaises(ValidationError):
            board.full_clean()

    def test_board_title_max_length(self):
        max_length_title = 'x' * 100
        board = Board(title=max_length_title)
        board.full_clean()

    def test_delete_board_that_has_lists(self):
        List.objects.create(title='Test List', board=self.board)
        self.assertEqual(Board.objects.count(), 1)
        self.board.delete()
        self.assertEqual(Board.objects.count(), 0)
        self.assertEqual(List.objects.count(), 0)


class ListModelTest(TestCase):
    def setUp(self):
        self.board = Board.objects.create(title='Test Board')
        self.list = List.objects.create(title='Test List', board=self.board)

    def test_list_creation(self):
        self.assertEqual(self.list.title, 'Test List')
        self.assertEqual(self.list.board, self.board)

    def test_list_title_over_max_length(self):
        long_title = 'x' * 101
        list = List(title=long_title, board=self.board)
        with self.assertRaises(ValidationError):
            list.full_clean()

    def test_list_title_max_length(self):
        max_length_title = 'x' * 100
        list = List(title=max_length_title, board=self.board)
        list.full_clean()

    def test_list_title_is_required(self):
        list = List(board=self.board)
        with self.assertRaises(ValidationError):
            list.full_clean()

    def test_list_get_next_position(self):
        self.assertEqual(self.list.get_next_position(), 0)
        task1 = Task.objects.create(title='Test Task 1', list=self.list, position=0)
        self.assertEqual(self.list.get_next_position(), 1)
        task2 = Task.objects.create(title='Test Task 2', list=self.list, position=4)
        self.assertEqual(self.list.get_next_position(), 5)
        task2.delete()
        self.assertEqual(self.list.get_next_position(), 1)

    def test_deleting_list_does_not_removes_board(self):
        self.assertEqual(Board.objects.count(), 1)
        self.list.delete()
        self.assertEqual(Board.objects.count(), 1)


class TaskModelTest(TestCase):
    def setUp(self):
        self.board = Board.objects.create(title='Test Board')
        self.list = List.objects.create(title='Test List', board=self.board)
        self.task = Task.objects.create(title='Test Task', list=self.list, position=5)

    def test_task_creation(self):
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(self.task.list, self.list)
        self.assertEqual(self.task.position, 5)

    def task_title_over_max_length(self):
        long_title = 'x' * 101
        task = Task(title=long_title, list=self.list, position=5)
        with self.assertRaises(ValidationError):
            task.full_clean()

    def task_title_max_length(self):
        max_length_title = 'x' * 100
        task = Task(title=max_length_title, list=self.list, position=5)
        task.full_clean()

    def test_task_title_is_required(self):
        task = Task(list=self.list, position=5)
        with self.assertRaises(ValidationError):
            task.full_clean()

    def test_task_position_default_value(self):
        task = Task(title='Test Task', list=self.list)
        self.assertEqual(task.position, 0)
                         

    def test_task_description_is_optional(self):
        task = Task(title='Test Task', list=self.list, position=5)
        task.full_clean()

    def test_task_description_max_length(self):
        max_length_description = 'x' * 500
        task = Task(title='Test Task', list=self.list, position=5, description=max_length_description)
        task.full_clean()

    def test_task_description_over_max_length(self):
        long_description = 'x' * 501
        task = Task(title='Test Task', list=self.list, position=5, description=long_description)
        with self.assertRaises(ValidationError):
            task.full_clean()


