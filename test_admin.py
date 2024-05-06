import pytest
from flask import session, redirect, url_for

from admin import app, Elections
from unittest.mock import patch, MagicMock
from PIL import Image
import base64
import random
@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_login_success(client):
    def mock_execute(query, params):
        if 'SELECT * FROM Admin WHERE CitizenID' in query:
            return [(11111111111, )]  # assume citizen exists
        else:
            return None

    with patch('admin.sqlite3.connect') as mock_connect:
        mock_cursor = mock_connect.return_value.cursor.return_value
        mock_cursor.execute.side_effect = mock_execute

        response = client.post('/', data={'admin_id': '11111111111'})
        assert response.status_code == 200


def test_login_fail(client):
    """Test the voting fingerprint page with a failed request."""
    response = client.post('/', data={'admin_id': '1111111'})
    assert response.status_code == 200
    assert b'Admin does not exist!' in response.data


def test_admin_main_page_with_admin_id_in_session(monkeypatch):
    # Set up a mock session with 'adminID' present
    monkeypatch.setitem(session, 'adminID', '11111111111')

    # Call the function and check if it returns the expected template
    assert AdminMainPage() == "admin_main.html"

def test_admin_main_page_without_admin_id_in_session(monkeypatch):
    if 'adminID' in session:
        del session['adminID']
    assert AdminMainPage() == redirect(url_for('Login'))


def test_admin_elections(client):
    with patch('admin.sqlite3') as sqlite3_mock:
        connection_mock = sqlite3_mock.connect.return_value
        cursor_mock = connection_mock.cursor.return_value
        cursor_mock.fetchall.return_value = [(20241, None,'2024-06-07','09:00:00','election1','2024-06-08','10:00:00'), (20242, None,'2024-06-07','09:00:00','election2','2024-06-08','10:00:00')]  # Sample data

        with patch('admin.render_template') as render_template_mock:
            # Call the function within the context of the patched modules
            result = Elections()

            # Check if database interaction was simulated correctly
            sqlite3_mock.connect.assert_called_once_with('Government')
            connection_mock.cursor.assert_called_once()
            cursor_mock.execute.assert_called_once_with('SELECT * FROM Election')

            # Check if render_template was called with the correct arguments
            render_template_mock.assert_called_once_with('elections.html',
                                                         elections=[(20241, None,'2024-06-07','09:00:00','election1','2024-06-08','10:00:00'), (20242, None,'2024-06-07','09:00:00','election2','2024-06-08','10:00:00')])

            # Check if the function returns the expected result
            assert result == render_template_mock.return_value

def test_add_election(client):
    with patch('admin.sqlite3') as sqlite3_mock:
        cursor_mock = sqlite3_mock.connect.return_value.cursor.return_value

        # Simulate a GET request to the AddElection page
        response_get = client.get('/elections/add')

        # Check if the response status code is 200 (OK)
        assert response_get.status_code == 200
        assert b'Add Election' in response_get.data  # Assuming 'Add Election' is in the page content

        # Simulate a POST request with form data
        form_data = {
            'description': 'Sample Election',
            'date': '2024-05-01',
            'time': '12:00 PM',
            'endDate': '2024-05-02',
            'endTime': '12:00 PM'
        }
        response_post = client.post('/elections/add', data=form_data, follow_redirects=True)

        # Check if the response redirects to the Elections page
        assert response_post.status_code == 200
        assert b'Election 1' in response_post.data  # Assuming 'Election 1' is in the page content

        # Check if the election data was added to the database
        cursor_mock.execute.assert_called_once_with(
            "INSERT INTO Election (Result,DateOfElection,ElectionTime,Description,EndDate,EndTime) VALUES(?, ?, ?, ?, ?, ?)",
            (None, '2024-05-01', '12:00 PM', 'Sample Election', '2024-05-02', '12:00 PM')
        )
        sqlite3_mock.connect.return_value.commit.assert_called_once()