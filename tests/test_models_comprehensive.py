"""Comprehensive tests for Device model with hostname and manufacturer fields."""

import pytest
import datetime
from unittest.mock import patch
from simple_scanner.models import Device


class TestDeviceHostnameManufacturer:
    """Comprehensive tests for Device model with new fields."""

    def test_device_creation_with_all_fields(self):
        """Test device creation with hostname and manufacturer."""
        now = datetime.datetime.now(datetime.timezone.utc)
        device = Device(
            mac_address="AA:BB:CC:DD:EE:FF",
            ip_address="192.168.1.100",
            hostname="my-laptop.local",
            manufacturer="Apple Inc.",
            date_added=now,
            last_seen=now
        )
        
        assert device.mac_address == "aa:bb:cc:dd:ee:ff"  # Normalized to lowercase
        assert device.ip_address == "192.168.1.100"
        assert device.hostname == "my-laptop.local"
        assert device.manufacturer == "Apple Inc."
        assert device.date_added == now
        assert device.last_seen == now

    def test_device_creation_minimal_fields(self):
        """Test device creation with only required fields."""
        device = Device(
            mac_address="AA:BB:CC:DD:EE:FF",
            ip_address="192.168.1.100"
        )
        
        assert device.mac_address == "aa:bb:cc:dd:ee:ff"
        assert device.ip_address == "192.168.1.100"
        assert device.hostname is None
        assert device.manufacturer is None
        assert isinstance(device.date_added, datetime.datetime)
        assert isinstance(device.last_seen, datetime.datetime)

    def test_device_creation_partial_fields(self):
        """Test device creation with some optional fields."""
        device = Device(
            mac_address="AA:BB:CC:DD:EE:FF",
            ip_address="192.168.1.100",
            hostname="server.example.com"
        )
        
        assert device.hostname == "server.example.com"
        assert device.manufacturer is None

    def test_update_hostname(self):
        """Test updating device hostname."""
        device = Device("aa:bb:cc:dd:ee:ff", "192.168.1.100")
        
        # Initially None
        assert device.hostname is None
        
        # Update to a value
        device.update_hostname("desktop-001")
        assert device.hostname == "desktop-001"
        
        # Update to another value
        device.update_hostname("desktop-001.local")
        assert device.hostname == "desktop-001.local"
        
        # Update to None
        device.update_hostname(None)
        assert device.hostname is None

    def test_update_manufacturer(self):
        """Test updating device manufacturer."""
        device = Device("aa:bb:cc:dd:ee:ff", "192.168.1.100")
        
        # Initially None
        assert device.manufacturer is None
        
        # Update to a value
        device.update_manufacturer("Dell Inc.")
        assert device.manufacturer == "Dell Inc."
        
        # Update to another value
        device.update_manufacturer("Dell Technologies")
        assert device.manufacturer == "Dell Technologies"
        
        # Update to None
        device.update_manufacturer(None)
        assert device.manufacturer is None

    def test_to_dict_with_all_fields(self):
        """Test dictionary representation with all fields."""
        now = datetime.datetime.now(datetime.timezone.utc)
        device = Device(
            mac_address="aa:bb:cc:dd:ee:ff",
            ip_address="192.168.1.100",
            hostname="workstation.lan",
            manufacturer="Lenovo",
            date_added=now,
            last_seen=now
        )
        
        result = device.to_dict()
        
        assert result['mac_address'] == "aa:bb:cc:dd:ee:ff"
        assert result['ip_address'] == "192.168.1.100"
        assert result['hostname'] == "workstation.lan"
        assert result['manufacturer'] == "Lenovo"
        assert result['date_added'] == now.isoformat()
        assert result['last_seen'] == now.isoformat()

    def test_to_dict_with_none_fields(self):
        """Test dictionary representation with None fields."""
        device = Device("aa:bb:cc:dd:ee:ff", "192.168.1.100")
        
        result = device.to_dict()
        
        assert result['hostname'] is None
        assert result['manufacturer'] is None

    def test_str_representation_all_fields(self):
        """Test string representation with all fields."""
        now = datetime.datetime.now(datetime.timezone.utc)
        device = Device(
            mac_address="aa:bb:cc:dd:ee:ff",
            ip_address="192.168.1.100",
            hostname="router.home",
            manufacturer="Netgear",
            date_added=now,
            last_seen=now
        )
        
        result = str(device)
        
        assert "MAC: aa:bb:cc:dd:ee:ff" in result
        assert "IP: 192.168.1.100" in result
        assert "Hostname: router.home" in result
        assert "Manufacturer: Netgear" in result
        assert now.isoformat() in result

    def test_str_representation_minimal_fields(self):
        """Test string representation with minimal fields."""
        device = Device("aa:bb:cc:dd:ee:ff", "192.168.1.100")
        
        result = str(device)
        
        assert "MAC: aa:bb:cc:dd:ee:ff" in result
        assert "IP: 192.168.1.100" in result
        assert "Hostname:" not in result  # Should not include if None
        assert "Manufacturer:" not in result  # Should not include if None

    def test_str_representation_partial_fields(self):
        """Test string representation with some optional fields."""
        device = Device(
            mac_address="aa:bb:cc:dd:ee:ff",
            ip_address="192.168.1.100",
            manufacturer="Unknown"
        )
        
        result = str(device)
        
        assert "Hostname:" not in result
        assert "Manufacturer: Unknown" in result

    def test_mac_address_case_normalization(self):
        """Test that MAC addresses are normalized to lowercase."""
        test_cases = [
            "AA:BB:CC:DD:EE:FF",
            "aa:bb:cc:dd:ee:ff",
            "Aa:Bb:Cc:Dd:Ee:Ff",
            "aA:bB:cC:dD:eE:fF"
        ]
        
        for mac in test_cases:
            device = Device(mac, "192.168.1.100")
            assert device.mac_address == "aa:bb:cc:dd:ee:ff"

    def test_field_types(self):
        """Test that fields have correct types."""
        device = Device(
            mac_address="aa:bb:cc:dd:ee:ff",
            ip_address="192.168.1.100",
            hostname="test.local",
            manufacturer="Test Corp"
        )
        
        assert isinstance(device.mac_address, str)
        assert isinstance(device.ip_address, str)
        assert isinstance(device.hostname, str)
        assert isinstance(device.manufacturer, str)
        assert isinstance(device.date_added, datetime.datetime)
        assert isinstance(device.last_seen, datetime.datetime)

    def test_hostname_special_characters(self):
        """Test hostname with special characters."""
        special_hostnames = [
            "server-001.example.com",
            "my_device.local",
            "192-168-1-100.dynamic.isp.com",
            "laptop.subdomain.example.co.uk",
            "device-with-very-long-hostname-that-might-appear.local"
        ]
        
        for hostname in special_hostnames:
            device = Device("aa:bb:cc:dd:ee:ff", "192.168.1.100", hostname=hostname)
            assert device.hostname == hostname

    def test_manufacturer_special_characters(self):
        """Test manufacturer with special characters."""
        special_manufacturers = [
            "Apple, Inc.",
            "Dell Inc.",
            "TP-LINK TECHNOLOGIES CO.,LTD.",
            "ASUSTek COMPUTER INC.",
            "Micro-Star INTL CO., LTD.",
            "Samsung Electronics Co.,Ltd",
            "Xiaomi Communications Co Ltd",
            "HUAWEI TECHNOLOGIES CO.,LTD"
        ]
        
        for manufacturer in special_manufacturers:
            device = Device("aa:bb:cc:dd:ee:ff", "192.168.1.100", manufacturer=manufacturer)
            assert device.manufacturer == manufacturer

    def test_empty_string_fields(self):
        """Test behavior with empty string fields."""
        device = Device(
            mac_address="aa:bb:cc:dd:ee:ff",
            ip_address="192.168.1.100",
            hostname="",
            manufacturer=""
        )
        
        # Empty strings should be stored as-is
        assert device.hostname == ""
        assert device.manufacturer == ""
        
        # String representation should NOT include empty strings
        result = str(device)
        assert "Hostname:" not in result  # Empty hostname not shown
        assert "Manufacturer:" not in result  # Empty manufacturer not shown

    def test_update_multiple_fields(self):
        """Test updating multiple fields in sequence."""
        device = Device("aa:bb:cc:dd:ee:ff", "192.168.1.100")
        original_date = device.date_added
        
        # Sleep briefly to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        # Update all fields
        device.update_ip_address("192.168.1.200")
        device.update_hostname("new-device.local")
        device.update_manufacturer("New Manufacturer")
        device.update_last_seen()
        
        assert device.ip_address == "192.168.1.200"
        assert device.hostname == "new-device.local"
        assert device.manufacturer == "New Manufacturer"
        assert device.last_seen > original_date

    def test_serialization_deserialization(self):
        """Test that device can be serialized and deserialized."""
        original = Device(
            mac_address="aa:bb:cc:dd:ee:ff",
            ip_address="192.168.1.100",
            hostname="test.local",
            manufacturer="Test Inc."
        )
        
        # Serialize
        data = original.to_dict()
        
        # Deserialize
        restored = Device(
            mac_address=data['mac_address'],
            ip_address=data['ip_address'],
            hostname=data['hostname'],
            manufacturer=data['manufacturer'],
            date_added=datetime.datetime.fromisoformat(data['date_added']),
            last_seen=datetime.datetime.fromisoformat(data['last_seen'])
        )
        
        assert restored.mac_address == original.mac_address
        assert restored.ip_address == original.ip_address
        assert restored.hostname == original.hostname
        assert restored.manufacturer == original.manufacturer
        assert restored.date_added == original.date_added
        assert restored.last_seen == original.last_seen

    @pytest.mark.parametrize("hostname,expected", [
        (None, None),
        ("", ""),
        ("localhost", "localhost"),
        ("device.local", "device.local"),
        ("192.168.1.1", "192.168.1.1"),
        ("my-device-001", "my-device-001"),
        ("UPPERCASE.LOCAL", "UPPERCASE.LOCAL"),  # Hostname case is preserved
    ])
    def test_hostname_variations(self, hostname, expected):
        """Test various hostname inputs."""
        device = Device("aa:bb:cc:dd:ee:ff", "192.168.1.100", hostname=hostname)
        assert device.hostname == expected

    @pytest.mark.parametrize("manufacturer,expected", [
        (None, None),
        ("", ""),
        ("Unknown", "Unknown"),
        ("Apple Inc.", "Apple Inc."),
        ("DELL INC.", "DELL INC."),  # Manufacturer case is preserved
        ("3Com", "3Com"),
        ("D-Link Corporation", "D-Link Corporation"),
    ])
    def test_manufacturer_variations(self, manufacturer, expected):
        """Test various manufacturer inputs."""
        device = Device("aa:bb:cc:dd:ee:ff", "192.168.1.100", manufacturer=manufacturer)
        assert device.manufacturer == expected