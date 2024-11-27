import pytest
import requests
import subprocess

@pytest.fixture(scope="session", autouse=True)
def initialize_database():
    """Run the initiate_db.py script inside the application container."""
    try:
        print("Initializing the database...")
        result = subprocess.run(
            ["docker", "compose", "run", "app", "python", "src/initiate_db.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        print(result.stdout)
        print(result.stderr)
        assert result.returncode == 0, "Database initialization failed"
    finally:
        print("Database initialization completed. Containers will not be shut down.")

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
    print("Response status code:", response.status_code)
    print("Response body:", response.text)
    assert response.status_code == 200, "Login page did not respond correctly"
    assert "Welcome back!" in response.text, "Login page content missing"

def test_register_endpoint(base_url):
    """Test the register page endpoint."""
    response = requests.get(base_url + "/register")
    assert response.status_code == 200, "Register page did not respond correctly"
    assert "Register Page" in response.text, "Register page content missing"
