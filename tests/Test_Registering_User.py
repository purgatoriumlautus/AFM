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

@pytest.fixture(scope="session")
def base_url(initialize_database):
    """Base URL for the application."""
    return "http://localhost:5000"

def test_register_and_login_user(base_url):
    """Test user registration and login functionality."""
    register_url = f"{base_url}/register"
    login_url = f"{base_url}/login"
    delete_user_url = f"{base_url}/delete-user"
    
    user_data = {
        "username": "testuser",
        "password": "testpassword",
        "email": "testuser@example.com"
    }

    # Step 1: Register the user
    register_response = requests.post(register_url, data=user_data)
    assert register_response.status_code == 200, "User registration failed"

    # Step 2: Login with the registered user credentials
    login_response = requests.post(login_url, data={
        "username": user_data["username"],
        "password": user_data["password"]
    })
    assert login_response.status_code == 200, "User login failed"
    assert "Welcome" in login_response.text or login_response.url.endswith("/"), "Login did not redirect to the main page"

    # # Step 3: Clean up by deleting the user
    # delete_response = requests.post(delete_user_url, data={"username": user_data["username"]})
    # assert delete_response.status_code == 200, "User deletion failed"
