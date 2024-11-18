import docker
import pytest
import logging

logging.basicConfig(level=logging.INFO)

@pytest.fixture(scope="module")
def docker_client():
    """Provide a Docker client instance."""
    return docker.from_env()

def test_dockerfile_build(docker_client):
    """Test if the Dockerfile builds successfully and the container runs."""
    try:
        logging.info("Building the Docker image...")
        image, logs = docker_client.images.build(path=".", tag="test-image")
        
        logging.info("Docker build logs:")
        for log in logs:
            if "stream" in log:
                print(log["stream"], end="")  # Print build logs for debugging

        assert image is not None, "Failed to build the Docker image"

        logging.info("Running the container...")
        container = docker_client.containers.run(
            "test-image", detach=True, ports={"5000/tcp": 5000}
        )
        container.reload()
        assert container.status == "running", "Container is not running"

        logging.info("Container is running successfully.")
        container.stop()
        container.remove()
    except docker.errors.BuildError as build_error:
        logging.error("BuildError encountered!")
        for log in build_error.build_log:
            if "stream" in log:
                logging.error(log["stream"])
        pytest.fail(f"Dockerfile test failed with BuildError: {build_error}")
    except Exception as e:
        logging.error(f"General error during the Dockerfile test: {e}")
        pytest.fail(f"Dockerfile test failed: {e}")
