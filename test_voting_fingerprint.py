import pytest
from fingerprintVotingSystem import app
import sqlite3
from unittest.mock import patch


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_voting_fingerprint_page_success(client):
    """Test the voting fingerprint page with a successful request."""
    response = client.post('/fingerprint', data={'voter_id': '55555555555'})
    assert response.status_code == 200
    assert b'<img src="data:image/png;base64,' in response.data


def test_voting_fingerprint_page_fail(client):
    """Test the voting fingerprint page with a failed request."""
    response = client.post('/fingerprint', data={'voter_id': '1111111'})
    assert response.status_code == 200
    assert b'Your ID does NOT exist!' in response.data


def test_voting_fingerprint_page_already_exist(client):
    def mock_execute(query, params):
        if 'SELECT * FROM Citizen WHERE CitizenID' in query:
            return [(11111111111,)]  # assume citizen exist
        elif 'SELECT * FROM Vote WHERE CitizenID' in query:
            return [(1,)]  # assume already voted
        else:
            return None

    with patch('fingerprintVotingSystem.sqlite3.connect') as mock_connect:
        mock_cursor = mock_connect.return_value.cursor.return_value
        mock_cursor.execute.side_effect = mock_execute

        with app.test_client() as client:
            response =client.post('/fingerprint', data={'CitizenID': '11111111111'})
            assert response.status_code ==200
            assert b'You have already voted!'