import pytest
import requests

# import subprocess  # Ensure subprocess is imported
# import time

# @pytest.fixture(scope="session", autouse=True)
# def start_docker_containers():
#     """Start the containers and ensure they are running."""
#     try:
#         # Start the containers
#         result = subprocess.run(
#             ["docker-compose", "up", "-d", "--build"],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True,
#         )
#         assert result.returncode == 0, f"docker-compose up failed: {result.stderr}"

#         # Wait for containers to initialize
#         time.sleep(10)  # Adjust based on your application's startup time

#         # Verify containers are running
#         result = subprocess.run(
#             ["docker-compose", "ps"],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True,
#         )
#         assert "Up" in result.stdout, f"Containers are not running: {result.stdout}"

#         # Yield to allow tests to run
#         yield

#     finally:
#         # Tear down containers after tests
#         print("Tearing down the containers")


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
