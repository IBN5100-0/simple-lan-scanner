"""Comprehensive tests for NetworkMonitor hostname and manufacturer parsing."""

import pytest
import datetime
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
from simple_scanner.scanner import NetworkMonitor
from simple_scanner.models import Device


class TestNetworkMonitorHostnameManufacturer:
    """Test NetworkMonitor's ability to parse hostname and manufacturer."""

    @pytest.fixture
    def nmap_output_with_hostname_manufacturer(self):
        """Sample nmap output with hostname and manufacturer."""
        return """Starting Nmap 7.93 ( https://nmap.org ) at 2023-01-01 12:00:00 EST
Nmap scan report for router.local (192.168.1.1)
Host is up (0.0010s latency).
MAC Address: 80:AF:CA:17:7A:78 (Cisco Systems)
Nmap scan report for desktop-001.local (192.168.1.100)
Host is up (0.0020s latency).
MAC Address: AA:BB:CC:DD:EE:FF (Dell Inc.)
Nmap scan report for 192.168.1.150
Host is up (0.0015s latency).
MAC Address: 11:22:33:44:55:66 (Unknown)
Nmap scan report for laptop.home (192.168.1.200)
Host is up (0.0025s latency).
MAC Address: 66:77:88:99:AA:BB (Apple, Inc.)
Nmap done: 256 IP addresses (4 hosts up) scanned in 2.50 seconds"""

    @pytest.fixture
    def nmap_output_mixed_formats(self):
        """Sample nmap output with various format variations."""
        return """Starting Nmap 7.93 ( https://nmap.org ) at 2023-01-01 12:00:00 EST
Nmap scan report for server.example.com (10.0.0.10)
Host is up (0.0010s latency).
MAC Address: AA:BB:CC:DD:EE:FF (DELL INC.)
Nmap scan report for 10.0.0.20
Host is up (0.0020s latency).
MAC Address: 11:22:33:44:55:66 (TP-LINK TECHNOLOGIES CO.,LTD.)
Nmap scan report for device-with-long-name.subdomain.example.local (10.0.0.30)
Host is up (0.0015s latency).
MAC Address: 77:88:99:AA:BB:CC (ASUSTek COMPUTER INC.)
Nmap scan report for 10.0.0.40
Host is up (0.0025s latency).
MAC Address: DD:EE:FF:00:11:22
Nmap done: 256 IP addresses (4 hosts up) scanned in 2.50 seconds"""

    @pytest.fixture
    def nmap_output_no_hostname(self):
        """Sample nmap output without hostnames."""
        return """Starting Nmap 7.93 ( https://nmap.org ) at 2023-01-01 12:00:00 EST
Nmap scan report for 192.168.1.1
Host is up (0.0010s latency).
MAC Address: 80:AF:CA:17:7A:78 (Netgear)
Nmap scan report for 192.168.1.100
Host is up (0.0020s latency).
MAC Address: AA:BB:CC:DD:EE:FF (Intel Corporate)
Nmap done: 256 IP addresses (2 hosts up) scanned in 2.50 seconds"""

    def test_parse_hostname_and_manufacturer(self, mock_nmap_executable, nmap_output_with_hostname_manufacturer):
        """Test parsing of hostname and manufacturer from nmap output."""
        with patch('simple_scanner.scanner.get_core_data_file') as mock_get_file:
            mock_get_file.return_value.exists.return_value = False
            monitor = NetworkMonitor(network='192.168.1.0/24', use_persistence=False)
        
        monitor._parse(nmap_output_with_hostname_manufacturer)
        devices = monitor.devices()
        
        assert len(devices) == 4
        
        # Check router
        router = next(d for d in devices if d.ip_address == '192.168.1.1')
        assert router.hostname == 'router.local'
        assert router.manufacturer == 'Cisco Systems'
        assert router.mac_address == '80:af:ca:17:7a:78'
        
        # Check desktop
        desktop = next(d for d in devices if d.ip_address == '192.168.1.100')
        assert desktop.hostname == 'desktop-001.local'
        assert desktop.manufacturer == 'Dell Inc.'
        assert desktop.mac_address == 'aa:bb:cc:dd:ee:ff'
        
        # Check device without hostname
        unknown = next(d for d in devices if d.ip_address == '192.168.1.150')
        assert unknown.hostname is None
        assert unknown.manufacturer == 'Unknown'
        assert unknown.mac_address == '11:22:33:44:55:66'
        
        # Check laptop
        laptop = next(d for d in devices if d.ip_address == '192.168.1.200')
        assert laptop.hostname == 'laptop.home'
        assert laptop.manufacturer == 'Apple, Inc.'
        assert laptop.mac_address == '66:77:88:99:aa:bb'

    def test_parse_mixed_formats(self, mock_nmap_executable, nmap_output_mixed_formats):
        """Test parsing various format variations."""
        with patch('simple_scanner.scanner.get_core_data_file') as mock_get_file:
            mock_get_file.return_value.exists.return_value = False
            monitor = NetworkMonitor(network='10.0.0.0/24', use_persistence=False)
        
        monitor._parse(nmap_output_mixed_formats)
        devices = monitor.devices()
        
        assert len(devices) == 4
        
        # Check long hostname
        long_name = next(d for d in devices if '10.0.0.30' in d.ip_address)
        assert long_name.hostname == 'device-with-long-name.subdomain.example.local'
        assert long_name.manufacturer == 'ASUSTek COMPUTER INC.'
        
        # Check device without manufacturer
        no_mfg = next(d for d in devices if d.ip_address == '10.0.0.40')
        assert no_mfg.hostname is None
        assert no_mfg.manufacturer is None

    def test_parse_no_hostname(self, mock_nmap_executable, nmap_output_no_hostname):
        """Test parsing when no hostnames are present."""
        with patch('simple_scanner.scanner.get_core_data_file') as mock_get_file:
            mock_get_file.return_value.exists.return_value = False
            monitor = NetworkMonitor(network='192.168.1.0/24', use_persistence=False)
        
        monitor._parse(nmap_output_no_hostname)
        devices = monitor.devices()
        
        assert len(devices) == 2
        
        for device in devices:
            assert device.hostname is None
            assert device.manufacturer is not None

    def test_hostname_manufacturer_persistence(self, mock_nmap_executable, tmp_path):
        """Test that hostname and manufacturer are persisted."""
        data_file = tmp_path / "devices.json"
        
        # Create parent directory if needed
        data_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initial scan with hostname and manufacturer
        initial_output = """Nmap scan report for server.local (192.168.1.100)
Host is up (0.001s latency).
MAC Address: AA:BB:CC:DD:EE:FF (Dell Inc.)"""
        
        # Create NetworkMonitor with persistence enabled and our test data file
        with patch('simple_scanner.scanner.get_core_data_file', return_value=data_file):
            monitor = NetworkMonitor(network='192.168.1.0/24', use_persistence=True)
            
            # Parse the output which should save to file
            monitor._parse(initial_output)
        
        # Verify data was saved
        assert data_file.exists(), "Data file should exist after parsing"
        with open(data_file, 'r') as f:
            saved_data = json.load(f)
        
        assert len(saved_data) == 1
        assert saved_data[0]['hostname'] == 'server.local'
        assert saved_data[0]['manufacturer'] == 'Dell Inc.'
        
        # Load in new monitor instance
        with patch('simple_scanner.scanner.get_core_data_file', return_value=data_file):
            monitor2 = NetworkMonitor(network='192.168.1.0/24', use_persistence=True)
        
        devices = monitor2.devices()
        assert len(devices) == 1
        assert devices[0].hostname == 'server.local'
        assert devices[0].manufacturer == 'Dell Inc.'

    def test_hostname_update(self, mock_nmap_executable):
        """Test updating hostname when it changes."""
        with patch('simple_scanner.scanner.get_core_data_file') as mock_get_file:
            mock_get_file.return_value.exists.return_value = False
            monitor = NetworkMonitor(network='192.168.1.0/24', use_persistence=False)
        
        # Initial scan without hostname
        output1 = """Nmap scan report for 192.168.1.100
Host is up (0.001s latency).
MAC Address: AA:BB:CC:DD:EE:FF (Dell Inc.)"""
        
        monitor._parse(output1)
        device = monitor.devices()[0]
        assert device.hostname is None
        
        # Second scan with hostname
        output2 = """Nmap scan report for myserver.local (192.168.1.100)
Host is up (0.001s latency).
MAC Address: AA:BB:CC:DD:EE:FF (Dell Inc.)"""
        
        monitor._parse(output2)
        device = monitor.devices()[0]
        assert device.hostname == 'myserver.local'

    def test_manufacturer_update(self, mock_nmap_executable):
        """Test updating manufacturer when it changes."""
        with patch('simple_scanner.scanner.get_core_data_file') as mock_get_file:
            mock_get_file.return_value.exists.return_value = False
            monitor = NetworkMonitor(network='192.168.1.0/24', use_persistence=False)
        
        # Initial scan with unknown manufacturer
        output1 = """Nmap scan report for 192.168.1.100
Host is up (0.001s latency).
MAC Address: AA:BB:CC:DD:EE:FF"""
        
        monitor._parse(output1)
        device = monitor.devices()[0]
        assert device.manufacturer is None
        
        # Second scan with manufacturer
        output2 = """Nmap scan report for 192.168.1.100
Host is up (0.001s latency).
MAC Address: AA:BB:CC:DD:EE:FF (HP Inc.)"""
        
        monitor._parse(output2)
        device = monitor.devices()[0]
        assert device.manufacturer == 'HP Inc.'

    def test_csv_export_with_new_fields(self, mock_nmap_executable, tmp_path):
        """Test CSV export includes hostname and manufacturer."""
        csv_file = tmp_path / "devices.csv"
        
        with patch('simple_scanner.scanner.get_core_data_file') as mock_get_file:
            mock_get_file.return_value.exists.return_value = False
            monitor = NetworkMonitor(network='192.168.1.0/24', use_persistence=False)
        
        output = """Nmap scan report for printer.office (192.168.1.50)
Host is up (0.001s latency).
MAC Address: AA:BB:CC:DD:EE:FF (Canon Inc.)
Nmap scan report for 192.168.1.60
Host is up (0.001s latency).
MAC Address: 11:22:33:44:55:66"""
        
        monitor._parse(output)
        monitor.to_csv(str(csv_file))
        
        # Read and verify CSV
        import csv
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 2
        
        # Check printer
        printer = next(r for r in rows if r['ip_address'] == '192.168.1.50')
        assert printer['hostname'] == 'printer.office'
        assert printer['manufacturer'] == 'Canon Inc.'
        
        # Check device without hostname/manufacturer
        device = next(r for r in rows if r['ip_address'] == '192.168.1.60')
        assert device['hostname'] == ''  # CSV empty string for None
        assert device['manufacturer'] == ''

    def test_json_export_with_new_fields(self, mock_nmap_executable, tmp_path):
        """Test JSON export includes hostname and manufacturer."""
        json_file = tmp_path / "devices.json"
        
        with patch('simple_scanner.scanner.get_core_data_file') as mock_get_file:
            mock_get_file.return_value.exists.return_value = False
            monitor = NetworkMonitor(network='192.168.1.0/24', use_persistence=False)
        
        output = """Nmap scan report for nas.home (192.168.1.80)
Host is up (0.001s latency).
MAC Address: AA:BB:CC:DD:EE:FF (Synology Incorporated)"""
        
        monitor._parse(output)
        monitor.to_json(str(json_file))
        
        # Read and verify JSON
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        assert len(data) == 1
        assert data[0]['hostname'] == 'nas.home'
        assert data[0]['manufacturer'] == 'Synology Incorporated'

    def test_special_characters_in_hostname(self, mock_nmap_executable):
        """Test parsing hostnames with special characters."""
        with patch('simple_scanner.scanner.get_core_data_file') as mock_get_file:
            mock_get_file.return_value.exists.return_value = False
            monitor = NetworkMonitor(network='192.168.1.0/24', use_persistence=False)
        
        output = """Nmap scan report for my-device_001.local (192.168.1.100)
Host is up (0.001s latency).
MAC Address: AA:BB:CC:DD:EE:FF (Test Corp)
Nmap scan report for device.sub-domain.example.com (192.168.1.101)
Host is up (0.001s latency).
MAC Address: 11:22:33:44:55:66 (Test Inc.)"""
        
        monitor._parse(output)
        devices = monitor.devices()
        
        assert devices[0].hostname == 'my-device_001.local'
        assert devices[1].hostname == 'device.sub-domain.example.com'

    def test_special_characters_in_manufacturer(self, mock_nmap_executable):
        """Test parsing manufacturers with special characters."""
        with patch('simple_scanner.scanner.get_core_data_file') as mock_get_file:
            mock_get_file.return_value.exists.return_value = False
            monitor = NetworkMonitor(network='192.168.1.0/24', use_persistence=False)
        
        output = """Nmap scan report for 192.168.1.100
Host is up (0.001s latency).
MAC Address: AA:BB:CC:DD:EE:FF (Samsung Electronics Co.,Ltd)
Nmap scan report for 192.168.1.101
Host is up (0.001s latency).
MAC Address: 11:22:33:44:55:66 (MICRO-STAR INTL CO., LTD.)"""
        
        monitor._parse(output)
        devices = monitor.devices()
        
        assert devices[0].manufacturer == 'Samsung Electronics Co.,Ltd'
        assert devices[1].manufacturer == 'MICRO-STAR INTL CO., LTD.'

    @pytest.mark.parametrize("nmap_line,expected_hostname,expected_ip", [
        ("Nmap scan report for router (192.168.1.1)", "router", "192.168.1.1"),
        ("Nmap scan report for my-device.local (10.0.0.100)", "my-device.local", "10.0.0.100"),
        ("Nmap scan report for 192.168.1.50", None, "192.168.1.50"),
        ("Nmap scan report for very-long-hostname-test.subdomain.example.com (172.16.0.10)", 
         "very-long-hostname-test.subdomain.example.com", "172.16.0.10"),
    ])
    def test_hostname_regex_variations(self, nmap_line, expected_hostname, expected_ip):
        """Test hostname regex with various inputs."""
        from simple_scanner.scanner import NetworkMonitor
        
        monitor = NetworkMonitor(network='192.168.1.0/24', use_persistence=False)
        match = monitor.HOST_REGEX.match(nmap_line)
        
        assert match is not None
        assert match.group('ip') == expected_ip
        assert match.group('hostname') == expected_hostname

    @pytest.mark.parametrize("mac_line,expected_mac,expected_mfg", [
        ("MAC Address: AA:BB:CC:DD:EE:FF (Apple Inc.)", "AA:BB:CC:DD:EE:FF", "Apple Inc."),
        ("MAC Address: 11:22:33:44:55:66 (Unknown)", "11:22:33:44:55:66", "Unknown"),
        ("MAC Address: 77:88:99:AA:BB:CC", "77:88:99:AA:BB:CC", None),
        ("MAC Address: DD:EE:FF:00:11:22 (TP-LINK TECHNOLOGIES CO.,LTD.)", 
         "DD:EE:FF:00:11:22", "TP-LINK TECHNOLOGIES CO.,LTD."),
    ])
    def test_mac_manufacturer_regex_variations(self, mac_line, expected_mac, expected_mfg):
        """Test MAC/manufacturer regex with various inputs."""
        from simple_scanner.scanner import NetworkMonitor
        
        monitor = NetworkMonitor(network='192.168.1.0/24', use_persistence=False)
        match = monitor.MAC_REGEX.match(mac_line)
        
        assert match is not None
        assert match.group('mac') == expected_mac
        assert match.group('manufacturer') == expected_mfg