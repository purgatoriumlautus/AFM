import pytest
import requests
import subprocess
from src.models import User
from src.app import create_app

def run_docker_command(cmd):
    """
    Helper function to execute a Docker command and return the result.
    Tries to run the command and handles exceptions like FileNotFoundError.
    """
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return result
    except FileNotFoundError:
        return None

@pytest.fixture(scope="session", autouse=True)
def initialize_database():
    """Run the initiate_db.py script inside the application container with a fallback for docker-compose."""
    try:
        print("Initializing the database...")

        # Define commands for modern and legacy Docker Compose
        docker_compose_cmd = ["docker", "compose", "run", "app", "python", "src/initiate_db.py"]
        docker_compose_legacy_cmd = ["docker-compose", "run", "app", "python", "src/initiate_db.py"]

        # Try modern Docker Compose command first
        result = run_docker_command(docker_compose_cmd)
        if not result or result.returncode != 0:
            print("`docker compose` failed. Trying `docker-compose` as fallback...")
            # Fallback to legacy Docker Compose command
            result = run_docker_command(docker_compose_legacy_cmd)

        # Log outputs for debugging
        if result:
            print(f"Command: {' '.join(result.args)}")
            print(f"Return Code: {result.returncode}")
            print(f"Stdout: {result.stdout}")
            print(f"Stderr: {result.stderr}")
            assert result.returncode == 0, "Database initialization failed"
        else:
            raise RuntimeError("Both `docker compose` and `docker-compose` commands failed to execute.")
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
        "password": "T3stP@ssw0rd!",
        "email": "testuser@example.com"
    }

    # Use `app.app_context()` explicitly
    with app.app_context():
        # Step 1: Register the user
        register_response = requests.post(register_url, data=user_data)
        assert register_response.status_code == 200, "User registration failed"

        # Step 2: Verify the user's email
        user = User.query.filter_by(username=user_data['username']).first()
        assert user is not None, "User was not found in the database"

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
