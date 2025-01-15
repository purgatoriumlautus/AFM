import pytest
import requests
import subprocess
from src.models import User
from src.app import create_app

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


def test_register_and_login_user():
    """Test user registration and login functionality."""
    app = create_app()
    base_url = "http://localhost:5000"
    register_url = f"{base_url}/register"
    login_url = f"{base_url}/login"

    user_data = {
        "username": "testuser",
        "password": "Testpassword1!",
        "email": "testuser@example.com",
        "home_address" : '48.408203429499316,15.587987069854968'
    }

    # Use `app.app_context()` explicitly
    with app.app_context():
        # Step 1: Register the user
        register_response = requests.post(register_url, data=user_data)
        assert register_response.status_code == 200, "User registration failed"

        # Step 2: Verify the user's email
        user = User.query.filter_by(username=user_data['username']).first()

        verify_url = f"{base_url}/verify/{user.uid}"
        verify_response = requests.get(verify_url)
        assert verify_response.status_code == 200, "Email verification failed"

        # Step 3: Login with the registered and verified user credentials
        login_response = requests.post(login_url, data={
            "username": user_data["username"],
            "password": user_data["password"]
        }, allow_redirects=True)
        assert login_response.status_code == 200, "User login failed"
        assert "Logged in successfully!" in login_response.text, f"Unexpected response: {login_response.text}"
