import pytest
from unittest.mock import Mock, patch, MagicMock

from src.db.db_worker import DatabaseWorker


class TestDatabaseWorkerCRUD:
    '''
    Tests for CRUD operations.
    '''

    def test_insert_data(self):
        worker = DatabaseWorker()
        worker._connection = Mock()
        worker._cursor = Mock()
        worker._cursor.fetchone.return_value = [1]

        result = worker.insert_data('test_table', {'name': 'Test'})

        assert result == 1
        worker._cursor.execute.assert_called_once()

    def test_update_data_success(self):
        worker = DatabaseWorker()
        worker._connection = Mock()
        worker._cursor = Mock()

        worker.update_data("test_table", {'name': 'Updated'}, 1)

        worker._cursor.execute.assert_called_once()

    def test_get_or_create_user_existing(self):
        worker = DatabaseWorker()
        worker._connection = Mock()
        worker._cursor = Mock()
        worker._cursor.fetchone.return_value = 5

        result = worker.get_or_create_user(
            {'email': 'testemail@domain.com'}
        )

        assert result == 5

    def test_get_or_create_user_new(self):
        worker = DatabaseWorker()
        worker._connection = Mock()
        worker._cursor = Mock()
        worker._cursor.fetchone.return_value = None

        with patch.object(worker, 'insert_data', return_value=10):
            result = worker.get_or_create_user(
                {'email': 'testemail@domain.com', 'name': 'firstname'}
            )

            assert result == 10
            worker.insert_data.assert_called_once()


class TestDatabaseWorkerPerevalOperations:
    '''
    Tests for operations with pereval data.
    '''

    @pytest.fixture
    def pereval_to_add(self):
        return {
            'beauty_title': 'Some beauty title',
            'title': 'Some common title',
            'other_titles': 'Some other titles',
            'connect': 'some connection',
            'add_time': '2026-07-01 12:00:00',
            'user': {
                'email': 'testemail@domain.com',
                'fam': 'Surname',
                'name': 'Firstname',
                'otc': 'Patronymic',
                'phone': '+7 999 999 99 99'
            },
            'coords': {
                'latitude': '99.123',
                'longitude': '123.12321',
                'height': '5544'
            },
            'level': {
                'winter': '1A',
                'spring': '2A',
                'autumn': '5B'
            },
            'images': [
                {
                    'data': 'some image',
                    'title': 'some image title'
                }
            ]
        }

    @pytest.fixture
    def mock_pereval(self):
        return {
            'id': 1,
            'beauty_title': 'Some beauty title',
            'title': 'Some common title',
            'other_titles': 'Some other titles',
            'connect': 'some connection',
            'status': 'new',
            'add_time': '2026-07-01 12:00:00',
            'date_added': '2026-07-01 12:00:00',
            'user': {
                'id': 1,
                'email': 'testemail@domain.com',
                'fam': 'Surname',
                'name': 'Firstname',
                'otc': 'Patronymic',
                'phone': '+7 999 999 99 99'
            },
            'coords': {
                'id': 1,
                'latitude': 99.123,
                'longitude': 123.12321,
                'height': 5544
            },
            'levels': {
                'id': 1,
                'winter': '1A',
                'spring': '2A',
                'summer': None,
                'autumn': '5B'
            },
            'images': [
                {
                    'id': 1,
                    'date_added': '2026-07-01 12:00:00',
                    'data': 'some image',
                    'title': 'some image title',
                    'pereval_id': 1
                }
            ]
        }

    def test_add_pereval(self, pereval_to_add):
        worker = DatabaseWorker()
        worker._connection = Mock()

        with patch.object(worker, 'get_or_create_user', return_value=1):
            with patch.object(worker, 'insert_data', side_effect=[1, 2, 3, 4]):
                result = worker.add_pereval(pereval_to_add)

                assert result == 3
                worker._connection.commit.assert_called_once()

    def test_update_pereval(self, mock_pereval):
        worker = DatabaseWorker()
        worker._connection = Mock()

        with patch.object(worker, 'update_data') as mock_update:
            state, message = worker.update_pereval(
                mock_pereval, 
                {'title': 'Updated title'}
            )
            
            assert state == 1
            assert message is None
            mock_update.assert_called_once()
            worker._connection.commit.assert_called_once()

    def test_get_pereval_by_id_success(self, mock_pereval):
        worker = DatabaseWorker()
        worker._connection = Mock()
        worker._dict_cursor = Mock()
        worker._dict_cursor.fetchone.return_value = mock_pereval

        result = worker.get_pereval_by_id(1)

        assert result == mock_pereval

    def test_get_pereval_by_id_not_found(self):
        worker = DatabaseWorker()
        worker._connection = Mock()
        worker._dict_cursor = Mock()
        worker._dict_cursor.fetchone.return_value = None

        result = worker.get_pereval_by_id(999)

        assert result is None

    def test_get_pereval_list_by_email_success(self):
        worker = DatabaseWorker()
        worker._connection = Mock()
        worker._cursor = Mock()
        worker._cursor.fetchall.return_value = [(1,)]

        with patch.object(
            worker, 
            'get_pereval_by_id', 
            return_value=self.mock_pereval
        ):
            result = worker.get_pereval_list_by_email('testemail@domain.com')

            assert len(result) == 1

    def test_get_pereval_list_by_email_empty(self):
        worker = DatabaseWorker()
        worker._connection = Mock()
        worker._cursor = Mock()
        worker._cursor.fetchall.return_value = []

        result = worker.get_pereval_list_by_email('testemail@domain.com')

        assert result == []