import docker
import pytest

@pytest.fixture(scope="module")
def docker_client():
    """Provide a Docker client instance."""
    return docker.from_env()

def test_dockerfile_build(docker_client):
    """Test if the Dockerfile builds successfully."""
    image, logs = docker_client.images.build(path=".", tag="test-image")
    assert image is not None, "Failed to build the Docker image"
