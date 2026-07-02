import pytest
from fastapi import status
from unittest.mock import patch


class TestSubmitDataEndpoint:
    '''
    Tests for "POST /SubmitData" endpoint
    '''

    @pytest.fixture
    def valid_data(self):
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
    def invalid_data(self):
        return {
            'beauty_title': 'Some beauty title',
            'title': 'Some common title',
            'add_time': 'invalid',
            'user': {
                'email': 'testemail@domain.com',
                'fam': 'Surname',
                'name': 'Firstname',
                'otc': 'Patronymic',
                'phone': '+7 999'
            },
            'coords': {
                'latitude': 'invalid',
                'longitude': '123.12321',
                'height': '5544'
            },
            'level': {},
            'images': [
                {
                    'data': 'some image',
                }
            ]
        }
    
    def test_success_response(self, client, valid_data):
        with patch('src.api.routes.DatabaseWorker') as mock_db_class:
            mock_db = mock_db_class.return_value
            mock_db.add_pereval.return_value = 1

            response = client.post('/submitData', json=valid_data)
            assert response.status_code == status.HTTP_200_OK
            assert response.json()['id'] == 1
            mock_db.connect.assert_called_once()
            mock_db.disconnect.assert_called_once()

    def test_bad_request_response(self, client, invalid_data):
        response = client.post('/submitData', json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert 'Error' in response.json()['message']


class TestGetPerevalByIdEndpoint:
    '''
    Tests for "GET /SubmitData/{id}" endpoint
    '''

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

    def test_success_response(self, client, mock_pereval):
        with patch('src.api.routes.DatabaseWorker') as mock_db_class:
            mock_db = mock_db_class.return_value
            mock_db.get_pereval_by_id.return_value = mock_pereval

            response = client.get('/submitData/1')

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data['id'] == 1
            assert data['beauty_title'] == 'Some beauty title'
            assert data['user']['email'] == 'testemail@domain.com'

    def test_not_found_response(self, client):
        with patch('src.api.routes.DatabaseWorker') as mock_db_class:
            mock_db = mock_db_class.return_value
            mock_db.get_pereval_by_id.return_value = None

            response = client.get('/submitData/999')
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert 'Object with id = 999 not found' in response.json()['message']


class TestPatchPerevalEndpoint:
    '''
    Tests for "PATCH /SubmitData/{id}" endpoint
    '''

    @pytest.fixture
    def mock_new_pereval(self):
        return {
            'id': 1,
            'beauty_title': 'Some beauty title',
            'title': 'Some common title',
            'status': 'new',
            'coords': {'id': 1},
            'levels': {'id': 1},
            'images': []
        }
    
    @pytest.fixture
    def mock_accepted_pereval(self):
        return {
            'id': 1,
            'beauty_title': 'Some beauty title',
            'title': 'Some common title',
            'status': 'accepted',
            'coords': {'id': 1},
            'levels': {'id': 1},
            'images': []
        }

    def test_empty_request(self, client):
        with patch('src.api.routes.DatabaseWorker') as mock_db_class:
            response = client.patch('/submitData/1', json={})

            assert response.status_code == status.HTTP_200_OK
            assert response.json()['state'] == 1
            assert response.json()['message'] is None

    def test_success_response(self, client, mock_new_pereval):
        with patch('src.api.routes.DatabaseWorker') as mock_db_class:
            mock_db = mock_db_class.return_value
            mock_db.get_pereval_by_id.return_value = mock_new_pereval
            mock_db.update_pereval.return_value = (1, None)

            response = client.patch('/submitData/1', json={'title': 'Updated title'})

            assert response.status_code == status.HTTP_200_OK
            assert response.json()['state'] == 1
            assert response.json()['message'] is None

    def test_not_found_response(self, client):
        with patch('src.api.routes.DatabaseWorker') as mock_db_class:
            mock_db = mock_db_class.return_value
            mock_db.get_pereval_by_id.return_value = None

            response = client.patch('/submitData/999', json={'title': 'Updated title'})

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json()['state'] == 0
            assert 'Pereval with id = 999 not found' in response.json()['message']

    def test_status_not_new_response(self, client, mock_accepted_pereval):
        with patch('src.api.routes.DatabaseWorker') as mock_db_class:
            mock_db = mock_db_class.return_value
            mock_db.get_pereval_by_id.return_value = mock_accepted_pereval

            response = client.patch('/submitData/1', json={'title': 'Updated Title'})

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()['state'] == 0
            assert 'Can`t update pereval with status other than "new"' in response.json()['message']


class TestGetUserPerevalsEndpoint:
    '''
    Tests for "GET /SubmitData/?user_email={email}" endpoint
    '''

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

    def test_success_response(self, client, mock_pereval):
        with patch('src.api.routes.DatabaseWorker') as mock_db_class:
            mock_db = mock_db_class.return_value
            mock_db.get_pereval_list_by_email.return_value = [
                mock_pereval,
                {**mock_pereval, 'id': 2}
            ]

            response = client.get('/submitData/?user_email=testemail@domain.com')

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 2
            assert data['1']['id'] == 1
            assert data['2']['id'] == 2

    def test_bad_request_response(self, client):
        response = client.get('/submitData/?user_email=1@a')
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert 'Error' in response.json()['message']

    def test_not_found_response(self, client, mock_pereval):
        with patch('src.api.routes.DatabaseWorker') as mock_db_class:
            mock_db = mock_db_class.return_value
            mock_db.get_pereval_list_by_email.return_value = []

            response = client.get('/submitData/?user_email=testemail@domain.com')
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert 'No objects found' in response.json()['message']
