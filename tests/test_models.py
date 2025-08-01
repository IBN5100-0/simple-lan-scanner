"""Tests for the Device model."""

import pytest
import datetime
from unittest.mock import patch
from simple_scanner.models import Device


class TestDevice:
    """Test cases for the Device class."""

    def test_device_creation_with_defaults(self, mock_datetime):
        """Test device creation with default timestamps."""
        with patch('datetime.datetime') as mock_dt:
            mock_dt.now.return_value = mock_datetime
            mock_dt.timezone = datetime.timezone
            
            device = Device("aa:bb:cc:dd:ee:ff", "192.168.1.100")
            
            assert device.mac_address == "aa:bb:cc:dd:ee:ff"
            assert device.ip_address == "192.168.1.100"
            assert device.hostname is None
            assert device.manufacturer is None
            assert device.date_added == mock_datetime
            assert device.last_seen == mock_datetime

    def test_device_creation_with_custom_timestamps(self):
        """Test device creation with custom timestamps."""
        date_added = datetime.datetime(2023, 1, 1, 10, 0, 0, tzinfo=datetime.timezone.utc)
        last_seen = datetime.datetime(2023, 1, 1, 11, 0, 0, tzinfo=datetime.timezone.utc)
        
        device = Device(
            "aa:bb:cc:dd:ee:ff", 
            "192.168.1.100", 
            date_added=date_added,
            last_seen=last_seen
        )
        
        assert device.mac_address == "aa:bb:cc:dd:ee:ff"
        assert device.ip_address == "192.168.1.100"
        assert device.date_added == date_added
        assert device.last_seen == last_seen

    def test_mac_address_normalization(self):
        """Test that MAC addresses are normalized to lowercase."""
        device = Device("AA:BB:CC:DD:EE:FF", "192.168.1.100")
        assert device.mac_address == "aa:bb:cc:dd:ee:ff"

    def test_update_last_seen_with_timestamp(self):
        """Test updating last seen with a specific timestamp."""
        device = Device("aa:bb:cc:dd:ee:ff", "192.168.1.100")
        new_timestamp = datetime.datetime(2023, 2, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
        
        device.update_last_seen(new_timestamp)
        
        assert device.last_seen == new_timestamp

    def test_update_last_seen_without_timestamp(self, mock_datetime):
        """Test updating last seen without providing timestamp."""
        device = Device("aa:bb:cc:dd:ee:ff", "192.168.1.100")
        
        with patch('datetime.datetime') as mock_dt:
            mock_dt.now.return_value = mock_datetime
            mock_dt.timezone = datetime.timezone
            
            device.update_last_seen()
            
            assert device.last_seen == mock_datetime

    def test_to_dict(self):
        """Test dictionary representation of device."""
        date_added = datetime.datetime(2023, 1, 1, 10, 0, 0, tzinfo=datetime.timezone.utc)
        last_seen = datetime.datetime(2023, 1, 1, 11, 0, 0, tzinfo=datetime.timezone.utc)
        
        device = Device(
            "aa:bb:cc:dd:ee:ff", 
            "192.168.1.100",
            date_added=date_added,
            last_seen=last_seen
        )
        
        result = device.to_dict()
        expected = {
            'mac_address': 'aa:bb:cc:dd:ee:ff',
            'ip_address': '192.168.1.100',
            'hostname': None,
            'manufacturer': None,
            'date_added': date_added.isoformat(),
            'last_seen': last_seen.isoformat()
        }
        
        assert result == expected

    def test_str_representation(self):
        """Test string representation of device."""
        date_added = datetime.datetime(2023, 1, 1, 10, 0, 0, tzinfo=datetime.timezone.utc)
        last_seen = datetime.datetime(2023, 1, 1, 11, 0, 0, tzinfo=datetime.timezone.utc)
        
        device = Device(
            "aa:bb:cc:dd:ee:ff", 
            "192.168.1.100",
            date_added=date_added,
            last_seen=last_seen
        )
        
        result = str(device)
        
        # Check the table-like format
        assert "aa:bb:cc:dd:ee:ff" in result
        assert "192.168.1.100" in result
        assert " | " in result  # Check for separator
        assert "-" in result  # Default value for hostname/manufacturer
        # Check date format (YYYY-MM-DD HH:MM) for local time
        import re
        assert re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', result) is not None

    def test_update_ip_address(self):
        """Test updating IP address."""
        device = Device("aa:bb:cc:dd:ee:ff", "192.168.1.100")
        
        device.update_ip_address("192.168.1.200")
        
        assert device.ip_address == "192.168.1.200"

