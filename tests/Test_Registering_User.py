import subprocess  # Ensure subprocess is imported
import time
import pytest
import requests

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

@pytest.fixture(scope="session")
def base_url(start_docker_containers):
    """Ensure the application is running before testing."""
    return "http://localhost:5000"

def test_user_registration(base_url):
    """Test user registration via the /register endpoint and delete the user after."""
    register_url = f"{base_url}/register"
    user_data = {
        "username": "testuser",
        "password": "testpassword",
        "email": "testuser@example.com"
    }

    # Step 1: Register the user
    response = requests.post(register_url, data=user_data)
    assert response.status_code == 200, "User registration failed"

    # Step 2: Verify user exists (optional)
    # If there's an endpoint to list users, uncomment the lines below:
    # response = requests.get(f"{base_url}/users")
    # assert "testuser" in response.text, "Registered user not found"

    # Step 3: Clean up by deleting the user
    delete_user_url = f"{base_url}/delete-user"
    delete_response = requests.post(delete_user_url, data={"username": "testuser"})
    assert delete_response.status_code == 200, "User deletion failed"
