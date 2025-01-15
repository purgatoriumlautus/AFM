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

