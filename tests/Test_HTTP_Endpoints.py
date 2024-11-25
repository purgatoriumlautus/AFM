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

def test_login_endpoint(base_url):
    """Test the login page endpoint."""
    response = requests.get(base_url + "/login")
    assert response.status_code == 200, "Login page did not respond correctly"
    assert "Login Page" in response.text, "Login page content missing"

def test_register_endpoint(base_url):
    """Test the register page endpoint."""
    response = requests.get(base_url + "/register")
    assert response.status_code == 200, "Register page did not respond correctly"
    assert "Register Page" in response.text, "Register page content missing"

def test_create_report_endpoint(base_url):
    """Test the create report page endpoint."""
    response = requests.get(base_url + "/create-report")
    assert response.status_code == 200, "Create report page did not respond correctly"
    assert "Your coordinates" in response.text, "Create report page content missing"

def test_view_reports_endpoint(base_url):
    """Test the view reports page endpoint."""
    response = requests.get(base_url + "/view-reports")
    assert response.status_code == 200, "View reports page did not respond correctly"
