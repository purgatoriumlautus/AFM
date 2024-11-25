import subprocess
import time
import pytest


def test_containers_running():
    """Test if containers in docker-compose.yaml start and are running."""
    try:
        # Start the containers
        result = subprocess.run(
            ["docker-compose", "up", "-d", "--build"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        assert result.returncode == 0, f"docker-compose up failed: {result.stderr}"

        # Wait a few seconds to ensure containers are running
        time.sleep(5)

        # Check if the containers are running
        result = subprocess.run(
            ["docker-compose", "ps"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        assert "Up" in result.stdout, f"One or more containers are not running: {result.stdout}"

    finally:
        # Tear down the containers after the test
        print("Tearing down the containers")
        # subprocess.run(["docker-compose", "down"])
