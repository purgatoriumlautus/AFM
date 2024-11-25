import pytest
import requests

@pytest.fixture(scope="module")
def base_url():
    """Base URL for the application."""
    return "http://localhost:5000"

def test_mainpage_endpoint(base_url):
    """Test the main page endpoint."""
    response = requests.get(base_url + "/")
    assert response.status_code == 200, "Main page did not respond correctly"
    assert "Austrian Flood Monitoring System" in response.text, "Main page content missing"
