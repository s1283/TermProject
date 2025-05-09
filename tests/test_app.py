import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_homepage_accessible(client):
    res = client.get('/')
    assert b'PUBLIC HOMEPAGE' in res.data
