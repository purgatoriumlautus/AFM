import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    """Base URL for the application."""
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
