import pytest

from fingerprintVotingSystem import app
import sqlite3
from unittest.mock import patch, MagicMock
from PIL import Image
import base64
import io
from faker import Faker
import random
@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_voting_fingerprint_page_success(client):
    def mock_execute(query, params):
        if 'SELECT * FROM Citizen WHERE CitizenID' in query:
            return [(55555555555, b'fingerprint_image_blob')]  # assume citizen exists
        elif 'SELECT * FROM Vote WHERE CitizenID' in query:
            return []  # assume citizen has not voted
        else:
            return None

    with patch('fingerprintVotingSystem.sqlite3.connect') as mock_connect:
        mock_cursor = mock_connect.return_value.cursor.return_value
        mock_cursor.execute.side_effect = mock_execute

        response = client.post('/fingerprint', data={'voter_id': '55555555555'})
        assert response.status_code == 200


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
            response = client.post('/fingerprint', data={'voter_id': '11111111111'})
            assert response.status_code == 200
            assert b'You have already voted!'


def test_voting_vote_page_success():
    # Use the existing app.test_client() as the Flask test client
    with app.test_client() as client:
        # Mock fingerprint file data
        with open('saved_image.bmp', 'rb') as image_file:
            image_data = image_file.read()

            # Patch the necessary functions and objects
            with patch('fingerprintVotingSystem.FingerPrintMatching.Check_Fingerprint', return_value=True):
                with patch('fingerprintVotingSystem.sqlite3.connect') as mock_connect:
                    # Mock database query results
                    person_data = (55555555555, "John", "Doe", "1990-01-01")
                    elections_data = [
                        (20244, "Election 1", "2024-04-13", "10:00"),
                        (20245, "Election 2", "2024-04-14", "12:00")
                    ]
                    mock_cursor = mock_connect.return_value.cursor.return_value
                    mock_cursor.fetchone.return_value = person_data
                    mock_cursor.fetchall.return_value = elections_data

                    # Create a file-like object from the image data
                    image_file = io.BytesIO(image_data)

                    # Send a POST request to the /vote endpoint with the file data
                    response = client.post('/vote', data={'voter_fingerprint': (image_file, 'saved_image.bmp')})

                    # Check if the response status code is 200 and if the expected template is in the response data
                    assert response.status_code == 200
                    assert b'voting_election_page.html' in response.data



def test_voting_vote_page_failure(client):
    path = 'saved_image.bmp'
    image = Image.open(path)
    with io.BytesIO() as output:
        image.save(output, format='PNG')
        blob = output.getvalue()
    with patch('fingerprintVotingSystem.FingerPrintMatching.Check_Fingerprint', return_value=False):
        with patch('fingerprintVotingSystem.sqlite3.connect') as mock_connect:
            mock_cursor = mock_connect.return_value.cursor.return_value
            mock_cursor.fetchone.return_value = None

            fingerprint_file = MagicMock()
            fingerprint_file.read.side_effect = lambda size: blob[:size]  # Modify lambda function to accept size argument

            response = client.post('/vote', data={'voter_fingerprint': fingerprint_file})

            assert response.status_code == 200
            assert b'voting_id_page.html' in response.data



def test_voting_candidate_page_success(client):
    # Mock election ID sent in the request form data
    election_id = 20241

    # Mock data returned from the database query
    candidates_data = [
        (33333333333, "Canberk", "Sefa"),
        (22222222222, "Adem", "Garip")
    ]

    # Mock database cursor behavior
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = candidates_data

    # Patch the necessary functions and objects
    with patch('fingerprintVotingSystem.sqlite3.connect') as mock_connect:
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Send a POST request to the /candidates endpoint with the correct form data
        response = client.post('/candidates', data={'election_id': str(election_id)})

        # Check if the response status code is 200
        assert response.status_code == 200

        # Check if each candidate's name and surname are present in the response data
        for candidate in candidates_data:
            assert candidate[1].encode() in response.data  # Candidate name
            assert candidate[2].encode() in response.data  # Candidate surname






def test_voting_candidate_page_fail():  # if it fails it has to give internal error
    # Mock election ID sent in the request form data
    election_id = '20241'

    # Mock database cursor behavior to raise an exception
    mock_cursor = MagicMock()
    mock_cursor.fetchall.side_effect = Exception('Database error')

    # Patch the necessary functions and objects
    with patch('fingerprintVotingSystem.sqlite3.connect') as mock_connect:
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Send a POST request to the /candidates endpoint with the election ID
        with app.test_client() as client:
            response = client.post('/candidates', data={'election_id': election_id})

            # Check if the response status code is 500 (Internal Server Error)
            assert response.status_code == 500
