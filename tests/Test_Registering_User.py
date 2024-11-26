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

    # Step 2: Clean up by deleting the user
    delete_user_url = f"{base_url}/delete-user"
    delete_response = requests.post(delete_user_url, data={"username": "testuser"})
    assert delete_response.status_code == 200, "User deletion failed"
