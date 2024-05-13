import pytest
from fingerprintVotingSystem import app as flask_app
from fingerprintVotingSystem import elections
import base64
import io
import datetime

from flask import session

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
    elections = []

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

def test_voting_fingerprint_page(client):
    """Test the voting_fingerprint_page route."""

    with client.session_transaction() as sess:
        sess['voter'] = '55555555555'

    # Simulate rendering the page after unsuccessful login
    response = client.post('/fingerprint', data={'voter_id': '12312312312'})
    assert response.status_code == 200
    assert b"Your ID does NOT exist!" in response.data
    # Simulate rendering the page after successful login
    response_post = client.post('/fingerprint', data={'voter_id': '55555555555'}, content_type='multipart/form-data', follow_redirects=True)
    #print(response_post.text)
    assert response_post.status_code == 200
    assert b"CHECK FINGERPRINT" in response_post.data

    with client.session_transaction() as sess:
        assert 'voter' in sess
        assert sess['voter'] == '55555555555'

## Testing authentication wrapper
#def test_protected_route_no_auth(client):
#    response = client.get("/vote")
#    assert response.status_code == 302  # Expecting a redirect to login page
#
## Test successful authentication scenario
#def test_protected_route_with_auth(client):
#    with client:
#        with client.session_transaction() as sess:
#            sess['voter'] = '55555555555'
#        response = client.get("/vote")
#        assert response.status_code in [200, 302]  # Valid session may still redirect or render a page
#
## Test the candidate page with POST method to simulate voting


def test_voting_vote_page(client):
    """Test the voting_vote_page route."""

    with client.session_transaction() as sess:
        sess['voter'] = '55555555555'
    # Reading mock fingerprint
    with open('C:\\Users\\gokbe\\Desktop\\Yeni klasör\\Fingerprint Voting System\\fingerprintVotingSystem\\ImageSent\\55555555555.bmp', 'rb') as img:
        image_base64 = img.read()

    data = {
        'voter_fingerprint': (io.BytesIO(image_base64), '55555555555.bmp')
    }
    # Simulate submitting the form with a fingerprint
    response = client.post('/vote', data=data, content_type='multipart/form-data', follow_redirects=True)
    #print(response.text)
    assert response.status_code == 200
    assert b"Election" in response.data

    with client.session_transaction() as sess:
        assert 'voter' in sess  # Ensure voter ID is still in session

def test_voting_candidate_page_post(client):
    """Test the voting_candidate_page route."""
    with client.session_transaction() as sess:
        sess['voter'] = '55555555555'

    # Simulate rendering the page after successful login with fingerprint
    response = client.post("/candidates", data={'election_id': '20241'})
    assert response.status_code == 200
    assert b"Candidate" in response.data
    assert b"Complete Voting" in response.data
    response_text = response.get_data(as_text=True)
    assert '33333333333' in response_text, "Candidate 'Canberk Sefa' not found in the response"
    # Simulate give a vote with mock candidate and ID after successful login with fingerprint
    response_select_candidate = client.post('/complete?election_id=20241', data={'election_id': '20241', 'candidate_id': '33333333333'}, follow_redirects=True)
    assert response_select_candidate.status_code == 200
    #print(response_select_candidate.text)
    assert b"Vote" in response_select_candidate.data
    assert b"Election" in response_select_candidate.data


def test_complete_voting(client):
    with client.session_transaction() as sess:
        sess['voter'] = '55555555555'
    # Simulate give all voting process with all mocks data after successful login with fingerprint
    response = client.post("/complete?election_id=20242", data=dict(candidate_id='44444444444'), follow_redirects=True)
    assert response.status_code == 200
    #print(response.text)
    assert b"Voting successfully completed." in response.data
