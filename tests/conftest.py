"""Pytest configuration and fixtures for simple_scanner tests."""

import pytest
import datetime
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch


@pytest.fixture
def sample_nmap_output():
    """Sample nmap output for testing parsing."""
    return """Starting Nmap 7.80 ( https://nmap.org ) at 2023-01-01 12:00 EST
Nmap scan report for 192.168.1.1
Host is up (0.001s latency).
MAC Address: AA:BB:CC:DD:EE:FF (Router Manufacturer)
Nmap scan report for 192.168.1.100
Host is up (0.002s latency).
MAC Address: 11:22:33:44:55:66 (Device Manufacturer)
Nmap scan report for hostname.local (192.168.1.50)
Host is up (0.003s latency).
MAC Address: 77:88:99:AA:BB:CC (Another Manufacturer)
Nmap done: 256 IP addresses (3 hosts up) scanned in 2.50 seconds"""


@pytest.fixture
def empty_nmap_output():
    """Empty nmap output for testing edge cases."""
    return """Starting Nmap 7.80 ( https://nmap.org ) at 2023-01-01 12:00 EST
Nmap done: 256 IP addresses (0 hosts up) scanned in 1.50 seconds"""


@pytest.fixture
def mock_datetime():
    """Fixed datetime for consistent testing."""
    return datetime.datetime(2023, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)


@pytest.fixture
def temp_output_file(tmp_path):
    """Temporary file for testing file operations."""
    return tmp_path / "test_output.json"


@pytest.fixture
def mock_nmap_executable():
    """Mock nmap executable path."""
    # Use platform-appropriate path
    if sys.platform == 'win32':
        nmap_path = 'C:\\Program Files\\Nmap\\nmap.exe'
    else:
        nmap_path = '/usr/bin/nmap'
    
    with patch('shutil.which', return_value=nmap_path):
        yield


@pytest.fixture
def mock_subprocess_success():
    """Mock successful subprocess.run call."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = ""
    mock_result.stderr = ""
    
    with patch('subprocess.run', return_value=mock_result) as mock_run:
        yield mock_run, mock_result


@pytest.fixture
def mock_subprocess_failure():
    """Mock failed subprocess.run call."""
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "Permission denied"
    
    with patch('subprocess.run', return_value=mock_result) as mock_run:
        yield mock_run, mock_result