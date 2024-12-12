import pytest
import requests
import subprocess

def run_docker_command(cmd):
    """
    Helper function to execute a Docker command and return the result.
    Tries to run the command and handles any exceptions like FileNotFoundError.
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
