"""
Pytest configuration and shared fixtures for ContactPlus tests
"""
import pytest
import asyncio
import docker
import httpx
import time
import tempfile
import shutil
from pathlib import Path


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def docker_client():
    """Docker client for container management tests"""
    return docker.from_env()


@pytest.fixture(scope="session")
def api_base_url():
    """Base URL for API tests"""
    return "http://localhost:8080/api/v1"


@pytest.fixture(scope="session")
def web_base_url():
    """Base URL for web interface tests"""
    return "http://localhost:3000"


@pytest.fixture(scope="session")
def monitor_base_url():
    """Base URL for monitor dashboard"""
    return "http://localhost:9090"


@pytest.fixture(scope="session")
def dozzle_base_url():
    """Base URL for Dozzle logs"""
    return "http://localhost:8081"


@pytest.fixture
async def api_client(api_base_url):
    """HTTP client for API testing"""
    async with httpx.AsyncClient(base_url=api_base_url, timeout=30.0) as client:
        yield client


@pytest.fixture
def test_vcard_data():
    """Sample vCard data for testing"""
    return """BEGIN:VCARD
VERSION:3.0
FN:John Doe
N:Doe;John;;;
EMAIL:john.doe@example.com
TEL:+1234567890
ORG:Test Company
TITLE:Software Engineer
NOTE:Test contact for unit testing
END:VCARD"""


@pytest.fixture
def multiple_test_vcards():
    """Multiple vCard contacts for bulk testing"""
    return """BEGIN:VCARD
VERSION:3.0
FN:Alice Smith
N:Smith;Alice;;;
EMAIL:alice@example.com
TEL:+1111111111
ORG:Tech Corp
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Bob Johnson
N:Johnson;Bob;;;
EMAIL:bob@example.com
TEL:+2222222222
ORG:Software Inc
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Carol Brown
N:Brown;Carol;;;
EMAIL:carol@example.com
TEL:+3333333333
ORG:Data Systems
END:VCARD"""


@pytest.fixture
def invalid_vcard_data():
    """Invalid vCard data for error testing"""
    return """BEGIN:VCARD
FN:Invalid Contact
EMAIL:invalid@example.com
END:VCARD"""  # Missing VERSION and proper structure


@pytest.fixture
def temp_vcard_file(test_vcard_data):
    """Temporary vCard file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.vcf', delete=False) as f:
        f.write(test_vcard_data)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        Path(temp_path).unlink()
    except FileNotFoundError:
        pass


@pytest.fixture
def temp_directory():
    """Temporary directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


def wait_for_service(url: str, timeout: int = 60) -> bool:
    """Wait for a service to become available"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            import requests
            response = requests.get(url, timeout=5)
            if response.status_code < 500:
                return True
        except:
            pass
        time.sleep(1)
    return False


@pytest.fixture(scope="session", autouse=True)
def wait_for_services():
    """Wait for all services to be ready before running tests"""
    services = [
        "http://localhost:8080/api/v1/health",
        "http://localhost:3000",
        "http://localhost:9090",
        "http://localhost:8081"
    ]
    
    for service_url in services:
        if not wait_for_service(service_url):
            pytest.skip(f"Service {service_url} not available")


@pytest.fixture
def sample_contact_data():
    """Sample contact data in API format"""
    return {
        "fn": "Test Contact",
        "emails": ["test@example.com"],
        "phones": ["+1234567890"],
        "organization": "Test Corp",
        "title": "Test Engineer",
        "notes": "Sample contact for testing"
    }