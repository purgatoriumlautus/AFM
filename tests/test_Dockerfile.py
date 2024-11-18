import docker
import pytest

@pytest.fixture(scope="module")
def docker_client():
    """Provide a Docker client instance."""
    return docker.from_env()

def test_dockerfile_build(docker_client):
    """Test if the Dockerfile builds successfully and the container runs."""
    try:
        # Build the Docker image
        image, logs = docker_client.images.build(path=".", tag="test-image")
        for log in logs:
            if "stream" in log:
                print(log["stream"], end="")  # Print build logs

        assert image is not None, "Failed to build the Docker image"

        # Run a container from the built image
        container = docker_client.containers.run(
            "test-image", detach=True, ports={"5000/tcp": 5000}
        )
        container.reload()
        assert container.status == "running", "Container is not running"
        
        # Stop the container after test
        container.stop()
        container.remove()
    except Exception as e:
        pytest.fail(f"Dockerfile test failed: {e}")
