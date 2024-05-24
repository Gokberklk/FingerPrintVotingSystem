from fingerprintVotingSystem import app as flask_app
from fingerprintVotingSystem import elections
import base64
import io
import datetime
import pytest
from unittest.mock import MagicMock
from PIL import Image



from flask import template_rendered, session

@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
    })
    yield flask_app

def setup_module(module):
    """Set up global state before running tests in this module."""
    global elections
    elections = [
        (20241, 'Null', datetime.date(2024, 6, 7), datetime.time(9, 0), None),
        (20242, 'Null', datetime.date(2024, 6, 7), datetime.time(9, 0), None)
    ]
def teardown_module(module):
    """Reset global state after running tests in this module."""
    global elections
    elections = [(20242, 'Null', datetime.date(2024, 6, 7), datetime.time(9, 0), None)]

@pytest.fixture
def client(app):
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    return client

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

def test_voting_id_page(client):
    """Test the voting_id_page route."""

    response = client.get("/")
    assert response.status_code == 200
    # Check for specific content or HTML elements that should appear in the page
    assert "Fingerprint Voting System" in response.get_data(as_text=True)
    assert "LOGIN" in response.get_data(as_text=True)  # Assuming "LOGIN" appears as part of the form
    # send a POST request to the 'voting_fingerprint_page' route
    response_post = client.post('/', data={'voter_id': '55555555555'})
    assert response_post.status_code == 200

from unittest.mock import patch


def test_voting_fingerprint_page(client):
    # It creates a mock connection with AWS RDS rather than a valid connection between line 62 to 64.
    # "cursor = AWS_connection.establish_connection()"
    with patch('fingerprintVotingSystem.AWS_connection.establish_connection') as mock_connection:
        cursor = MagicMock()
        mock_connection.return_value = cursor

        # Test scenario 1: Voter ID does not exist
        """ Since the entered ID will not be in the database, the values returned from the queries are empty. 
            fetchone: if a single value will be returned from the query
            fetchall: if more than one value will be returned from the query"""
        cursor.fetchone.return_value = None #cursor.execute("SELECT * FROM Citizen WHERE CitizenID = %s", (entered_id,))
        cursor.fetchall.return_value = [] #cursor.execute("SELECT * FROM Vote WHERE CitizenID = %s", (entered_id,))
        response = client.post('/fingerprint', data={'voter_id': '12312312312'}) #Invalid voter ID sent to fingerprint route
        """ 302 means that this status code indicates that further action needs to be taken by the user agent in order to fulfill the request.
            The reason for this is that the user is sent to the ID page again and asked to enter a valid ID again."""
        assert response.status_code == 302
        """ After running the response fingerprint route returned as a result of line 72, 
            the html as a text of the redirected page and the name of the route are returned."""
        assert b"/voting_id_page" in response.data

        # Mock data has been reset for the next test case.
        cursor.fetchone.reset_mock()
        cursor.fetchall.reset_mock()

        # Test scenario 2: Voter ID exists but has not voted
        """ If the ID entered is valid, the valid information coming from the database is entered between lines 89 and 92.
            Since we need images from the database on the page where the fingerprint will be read, 
            the get_dummy_image_bytes() method is created and sends an image in the form of a mock byte. 
            This was done for both the fingerprint and the citizen's own image."""
        cursor.fetchone.return_value = [55555555555, 'Ata', 'Öztaş', '1990-01-01', 'Eskişehir',
                                        get_dummy_image_bytes(),get_dummy_image_bytes()]
        # This query returns empty since it is assumed that the citizen has not voted before in the current election.
        cursor.fetchall.return_value = []
        # Valid ID has been sent to the fingerprint route.
        response = client.post('/fingerprint', data={'voter_id': '55555555555'})
        """ 200 means that this status code indicates that the client's request was successfully received, understood, and accepted.
            That's why the returning response includes the html and route name as vote page in text. """
        assert response.status_code == 200
        assert b"/vote" in response.data

        # Mock data has been reset for the next test case.
        cursor.fetchone.reset_mock()
        cursor.fetchall.reset_mock()

        # Test scenario 3: Voter ID exists and has already voted
        """ If the entered ID is valid but this citizen has previously voted in the current election, 
            the values in line 112 and coming from the database are returned as 1. 
            In other words, let's assume that two elections take place at the same time, 
            two tuples are returned as a list showing the voting rate in these elections. 
            """
        cursor.fetchone.return_value = [55555555555, 'Ata', 'Öztaş' , '1990-01-01', 'Eskişehir',
                                        get_dummy_image_bytes(), get_dummy_image_bytes()]
        cursor.fetchall.return_value = [(1,), (1,)]
        # Valid ID has been sent to the fingerprint route.
        response = client.post('/fingerprint', data={'voter_id': '55555555555'})
        assert response.status_code == 200
        assert b"You have already voted!" in response.data

#This method creates a byte image for mocking.
def get_dummy_image_bytes():
    # Create a simple image with PIL
    image = Image.new('RGB', (100, 100), color=(90, 100, 150))  #
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='bmp')
    img_byte_arr = img_byte_arr.getvalue()  # This is how the image would be stored as a blob in a database
    return img_byte_arr


def test_voting_vote_page(client):
    """Test the voting_vote_page route."""
    #It creates a mock connection with AWS RDS rather than a valid connection between line 108 to 111. "cursor = AWS_connection.establish_connection()"
    with patch('fingerprintVotingSystem.AWS_connection.establish_connection') as mock_connection:
        cursor = MagicMock()
        mock_connection.return_value = cursor
        #In order to remain in the system, a valid ID mock data is entered into the Session between line 112 to 113.
        with client.session_transaction() as sess:
            sess['voter'] = '55555555555'
        #
        with open('C:\\Users\\gokbe\\Desktop\\Yeni klasör\\Fingerprint Voting System\\fingerprintVotingSystem\\ImageSent\\valid.bmp', 'rb') as img:
            image_base64 = img.read()
        citizen_photo= get_dummy_image_bytes()
        cursor.fetchone.return_value = (55555555555, 'Ata', 'Öztaş', datetime.date(1900, 6, 6), 'Eskişehir', image_base64, citizen_photo)
        data = {
            'voter_fingerprint': (io.BytesIO(image_base64), '55555555555.bmp')
        }
        # Simulate submitting the form with a fingerprint
        response = client.post('/vote', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        assert b"Ata" in response.data
        assert b"55555555555" in response.data

        with client.session_transaction() as sess:
            assert 'voter' in sess
            assert sess['voter'] == '55555555555'

def test_voting_candidate_page_post(client):
    """Test the voting_candidate_page route."""
    with patch('fingerprintVotingSystem.AWS_connection.establish_connection') as mock_connection:
        cursor = MagicMock()
        mock_connection.return_value = cursor
        cursor.fetchall.return_value = [(None, 22222222222, 20241), (None, 33333333333, 20241)]
        cursor.fetchone.return_value = (22222222222, 'Adem', 'Garip', datetime.date(1900, 6, 6), 'Bursa', get_dummy_image_bytes(), get_dummy_image_bytes())
        cursor.fetchone.reset_mock()
        cursor.fetchone.return_value = (33333333333, 'Canberk', 'Sefa', datetime.date(1900, 6, 6), 'Bursa', get_dummy_image_bytes(), get_dummy_image_bytes())
        with client.session_transaction() as sess:
            sess['voter'] = '55555555555'

        # Simulate rendering the page after successful login with fingerprint
        response = client.post("/candidates", data={'election_id': '20241'})
        assert response.status_code == 200
        print(response.text)
        assert b"/complete?election_id=20241" in response.data
        response_text = response.get_data(as_text=True)
        # Simulate give a vote with mock candidate and ID after successful login with fingerprint
        response_select_candidate = client.post('/complete?election_id=20241', data={'election_id': '20241', 'candidate_id': '33333333333'}, follow_redirects=True)
        assert response_select_candidate.status_code == 200
        #print(response_select_candidate.text)
        assert '33333333333' in response_text, "Candidate 'Canberk Sefa' not found in the response"


def test_complete_voting(client):
    with patch('fingerprintVotingSystem.AWS_connection.establish_connection') as mock_connection:
        cursor = MagicMock()
        mock_connection.return_value = cursor
        with client.session_transaction() as sess:
            sess['voter'] = '55555555555'

        cursor.fetchall.return_value = [(None, 44444444444, 20242), (None, 55555555555, 20242)]
        cursor.fetchone.return_value = (
            44444444444, 'Osman Eren', 'Gündoğdu',
            datetime.date(1900, 6, 6),
            'Bursa', get_dummy_image_bytes(),
            get_dummy_image_bytes())
        cursor.fetchone.reset_mock()
        cursor.fetchone.return_value = (55555555555, 'Ata', 'Öztaş',
                                        datetime.date(1900, 6, 6),
                                        'Bursa', get_dummy_image_bytes(),
                                        get_dummy_image_bytes())
        # Simulate give all voting process with all mocks data after successful login with fingerprint
        response = client.post("/complete?election_id=20242", data=dict(candidate_id='44444444444'), follow_redirects=True)
        assert response.status_code == 200
        #print(response.text)
        assert b"Voting successfully completed." in response.data
















































"""
def test_voting_fingerprint_page2(mocker, client):


    # Mock the database connection and cursor
    mock_cursor = mocker.Mock()
    mock_connection = mocker.Mock()
    mock_connection.establish_connection.return_value = mock_cursor
    mocker.patch('fingerprintVotingSystem.AWS_connection.establish_connection')


    # Setup mock responses
    mock_cursor.fetchone.return_value = (55555555555, 'Ata', 'Öztaş', None, None, None)  # Adjust based on actual data structure
    mock_cursor.fetchall.return_value = []  # No votes cast yet

    print(mock_connection.fetchone)
    with client.session_transaction() as sess:
        sess['voter'] = '55555555555'

    # Simulate rendering the page after unsuccessful login
    mock_cursor.fetchone.return_value = None  # Adjust fetchone to return None for invalid ID
    response = client.post('/fingerprint', data={'voter_id': '12312312312'})
    assert response.status_code == 200
    assert b"Your ID does NOT exist!" in response.data

    # Simulate rendering the page after successful login
    mock_cursor.fetchone.return_value = (55555555555, 'Ata', 'Öztaş', None, None, None)
    response = client.post('/fingerprint', data={'voter_id': '55555555555'}, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert b"CHECK FINGERPRINT" in response.data

    # Check if SQL queries were correctly executed
    mock_cursor.execute.assert_any_call("SELECT * FROM Citizen WHERE CitizenID = %s", ('55555555555',))
    mock_cursor.execute.assert_any_call("SELECT * FROM Vote WHERE CitizenID = %s", ('55555555555',))


    # Check session clearing for already voted
    mock_cursor.fetchall.return_value = [('20241',), ('20242',)]  # Assuming 2 active elections
    response = client.post('/fingerprint', data={'voter_id': '55555555555'})
    assert b"You have already voted!" in response.data"""
