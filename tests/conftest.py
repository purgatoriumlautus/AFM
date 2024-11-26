import subprocess
import time
import pytest

@pytest.fixture(scope="session", autouse=True)
def start_docker_containers():
    """Start the containers and ensure they are running."""
    try:
        print("Starting Docker containers...")
        result = subprocess.run(
            ["docker-compose", "up", "-d", "--build"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        print(result.stdout)
        print(result.stderr)
        assert result.returncode == 0, f"docker-compose up failed: {result.stderr}"

        # Wait for containers to initialize
        time.sleep(10)

        # Verify containers are running
        result = subprocess.run(
            ["docker-compose", "ps"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        print(result.stdout)
        assert "Up" in result.stdout, f"Containers are not running: {result.stdout}"

        # Yield to allow tests to run
        yield
    finally:
        print("Tearing down Docker containers")
        subprocess.run(["docker-compose", "down"])
