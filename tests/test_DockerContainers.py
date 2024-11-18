import subprocess
import time
import logging
import pytest

logging.basicConfig(level=logging.INFO)

def test_containers_running():
    """Test if containers in docker-compose.yaml start and are running."""
    try:
        logging.info("Starting containers using docker-compose...")
        result = subprocess.run(
            ["docker-compose", "up", "-d", "--build"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        assert result.returncode == 0, f"docker-compose up failed: {result.stderr}"

        # Wait for services to initialize
        time.sleep(5)

        logging.info("Checking container statuses...")
        result = subprocess.run(
            ["docker-compose", "ps"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        assert "Up" in result.stdout, f"One or more containers are not running: {result.stdout}"
        
        # Add health check
        result = subprocess.run(
            ["docker-compose", "logs"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        assert "Error" not in result.stdout, "Containers encountered errors: check logs"
        
        logging.info("All containers are running successfully.")
    finally:
        logging.info("Tearing down containers...")
        subprocess.run(["docker-compose", "down"])
