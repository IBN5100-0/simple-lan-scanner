"""Tests for the NetworkMonitor scanner."""

import pytest
import json
import csv
import subprocess
import datetime
from unittest.mock import patch, MagicMock, call
from pathlib import Path

from simple_scanner.scanner import NetworkMonitor, autodetect_network
from simple_scanner.models import Device


class TestAutodetectNetwork:
    """Test cases for the autodetect_network function."""

    def test_autodetect_network_prefers_192_168(self):
        """Test that 192.168.x.x networks are preferred."""
        mock_ips = ['10.0.1.5', '172.16.1.5', '192.168.1.5']
        
        with patch('socket.gethostname', return_value='test-host'), \
             patch('socket.getaddrinfo') as mock_getaddrinfo:
            
            # Mock getaddrinfo to return our test IPs
            mock_getaddrinfo.return_value = [
                (None, None, None, None, (ip, None)) for ip in mock_ips
            ]
            
            result = autodetect_network()
            assert result == '192.168.1.0/24'

    def test_autodetect_network_falls_back_to_172(self):
        """Test fallback to 172.16-31.x.x networks."""
        mock_ips = ['10.0.1.5', '172.20.1.5']
        
        with patch('socket.gethostname', return_value='test-host'), \
             patch('socket.getaddrinfo') as mock_getaddrinfo:
            
            mock_getaddrinfo.return_value = [
                (None, None, None, None, (ip, None)) for ip in mock_ips
            ]
            
            result = autodetect_network()
            assert result == '172.20.1.0/24'

    def test_autodetect_network_falls_back_to_10(self):
        """Test fallback to 10.x.x.x networks."""
        mock_ips = ['10.0.1.5']
        
        with patch('socket.gethostname', return_value='test-host'), \
             patch('socket.getaddrinfo') as mock_getaddrinfo:
            
            mock_getaddrinfo.return_value = [
                (None, None, None, None, (ip, None)) for ip in mock_ips
            ]
            
            result = autodetect_network()
            assert result == '10.0.1.0/24'

    def test_autodetect_network_filters_unwanted_ips(self):
        """Test that unwanted IP ranges are filtered out."""
        mock_ips = ['169.254.1.5', '192.168.56.5', '192.168.1.5']
        
        with patch('socket.gethostname', return_value='test-host'), \
             patch('socket.getaddrinfo') as mock_getaddrinfo:
            
            mock_getaddrinfo.return_value = [
                (None, None, None, None, (ip, None)) for ip in mock_ips
            ]
            
            result = autodetect_network()
            assert result == '192.168.1.0/24'

    def test_autodetect_network_no_suitable_ip_raises_error(self):
        """Test that RuntimeError is raised when no suitable IP is found."""
        mock_ips = ['169.254.1.5', '192.168.56.5']  # Only unwanted IPs
        
        with patch('socket.gethostname', return_value='test-host'), \
             patch('socket.getaddrinfo') as mock_getaddrinfo:
            
            mock_getaddrinfo.return_value = [
                (None, None, None, None, (ip, None)) for ip in mock_ips
            ]
            
            with pytest.raises(RuntimeError, match="Could not find a suitable IPv4 address"):
                autodetect_network()


class TestNetworkMonitor:
    """Test cases for the NetworkMonitor class."""

    def test_init_with_custom_network(self, mock_nmap_executable):
        """Test NetworkMonitor initialization with custom network."""
        with patch('simple_scanner.scanner.get_core_data_file') as mock_get_file:
            mock_get_file.return_value.exists.return_value = False
            monitor = NetworkMonitor(network='10.0.0.0/24')
            assert monitor.network == '10.0.0.0/24'
            assert not monitor.remove_stale
            assert not monitor.verbose
            assert monitor.use_persistence

    def test_init_with_autodetect_network(self, mock_nmap_executable):
        """Test NetworkMonitor initialization with autodetected network."""
        with patch('simple_scanner.scanner.autodetect_network', return_value='192.168.1.0/24'), \
             patch('simple_scanner.scanner.get_core_data_file') as mock_get_file:
            mock_get_file.return_value.exists.return_value = False
            monitor = NetworkMonitor()
            assert monitor.network == '192.168.1.0/24'

    def test_init_nmap_not_found_raises_error(self):
        """Test that RuntimeError is raised when nmap is not found."""
        with patch('shutil.which', return_value=None):
            with pytest.raises(RuntimeError, match="nmap not found"):
                NetworkMonitor()

    def test_run_command_success(self, mock_nmap_executable, sample_nmap_output):
        """Test successful nmap command execution."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = sample_nmap_output
        mock_result.stderr = ""
        
        with patch('subprocess.run', return_value=mock_result):
            monitor = NetworkMonitor(network='192.168.1.0/24')
            result = monitor._run_command()
            
            assert result == sample_nmap_output

    def test_run_command_failure(self, mock_nmap_executable):
        """Test failed nmap command execution."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Permission denied"
        
        with patch('subprocess.run', return_value=mock_result):
            monitor = NetworkMonitor(network='192.168.1.0/24')
            
            with pytest.raises(RuntimeError, match="Nmap scan failed.*Permission denied"):
                monitor._run_command()

    def test_run_command_timeout(self, mock_nmap_executable):
        """Test nmap command timeout handling."""
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired('nmap', 300)):
            monitor = NetworkMonitor(network='192.168.1.0/24')
            
            with pytest.raises(RuntimeError, match="Nmap scan timed out"):
                monitor._run_command()

    def test_run_command_file_not_found(self, mock_nmap_executable):
        """Test handling of FileNotFoundError."""
        with patch('subprocess.run', side_effect=FileNotFoundError()):
            monitor = NetworkMonitor(network='192.168.1.0/24')
            
            with pytest.raises(RuntimeError, match="Nmap executable not found"):
                monitor._run_command()

    def test_run_command_permission_error(self, mock_nmap_executable):
        """Test handling of PermissionError."""
        with patch('subprocess.run', side_effect=PermissionError()):
            monitor = NetworkMonitor(network='192.168.1.0/24')
            
            with pytest.raises(RuntimeError, match="Permission denied running nmap"):
                monitor._run_command()

    def test_parse_nmap_output(self, mock_nmap_executable, sample_nmap_output, mock_datetime):
        """Test parsing of nmap output."""
        with patch('simple_scanner.scanner.get_core_data_file') as mock_get_file:
            mock_get_file.return_value.exists.return_value = False
            monitor = NetworkMonitor(network='192.168.1.0/24', use_persistence=False)
            
            with patch('datetime.datetime') as mock_dt:
                mock_dt.now.return_value = mock_datetime
                mock_dt.timezone = MagicMock()
                mock_dt.timezone.utc = mock_datetime.tzinfo
                
                monitor._parse(sample_nmap_output)
            
            devices = monitor.devices()
            assert len(devices) == 3
            
            # Check first device
            device1 = next(d for d in devices if d.mac_address == 'aa:bb:cc:dd:ee:ff')
            assert device1.ip_address == '192.168.1.1'
            
            # Check second device
            device2 = next(d for d in devices if d.mac_address == '11:22:33:44:55:66')
            assert device2.ip_address == '192.168.1.100'
            
            # Check third device
            device3 = next(d for d in devices if d.mac_address == '77:88:99:aa:bb:cc')
            assert device3.ip_address == '192.168.1.50'

    def test_parse_empty_output(self, mock_nmap_executable, empty_nmap_output):
        """Test parsing of empty nmap output."""
        with patch('simple_scanner.scanner.get_core_data_file') as mock_get_file:
            mock_get_file.return_value.exists.return_value = False
            monitor = NetworkMonitor(network='192.168.1.0/24', use_persistence=False)
            monitor._parse(empty_nmap_output)
        
        devices = monitor.devices()
        assert len(devices) == 0

    def test_parse_updates_existing_device(self, mock_nmap_executable, mock_datetime):
        """Test that existing devices are updated, not duplicated."""
        with patch('simple_scanner.scanner.get_core_data_file') as mock_get_file:
            mock_get_file.return_value.exists.return_value = False
            monitor = NetworkMonitor(network='192.168.1.0/24', use_persistence=False)
        
        # First parse
        first_output = """Nmap scan report for 192.168.1.1
Host is up (0.001s latency).
MAC Address: AA:BB:CC:DD:EE:FF (Manufacturer)"""
        
        with patch('datetime.datetime') as mock_dt:
            mock_dt.now.return_value = mock_datetime
            mock_dt.timezone = MagicMock()
            mock_dt.timezone.utc = mock_datetime.tzinfo
            
            monitor._parse(first_output)
            assert len(monitor.devices()) == 1
            
            # Second parse with same device
            monitor._parse(first_output)
            assert len(monitor.devices()) == 1  # Should still be 1

    def test_parse_with_remove_stale_enabled(self, mock_nmap_executable, mock_datetime):
        """Test that stale devices are removed when remove_stale is enabled."""
        with patch('simple_scanner.scanner.get_core_data_file') as mock_get_file:
            mock_get_file.return_value.exists.return_value = False
            monitor = NetworkMonitor(network='192.168.1.0/24', remove_stale=True, use_persistence=False)
        
        # Add a device manually
        with patch('datetime.datetime') as mock_dt:
            mock_dt.now.return_value = mock_datetime
            mock_dt.timezone = MagicMock()
            mock_dt.timezone.utc = mock_datetime.tzinfo
            
            monitor._devices['old:device:mac'] = Device('old:device:mac', '192.168.1.99')
            
            # Parse output that doesn't include the old device
            new_output = """Nmap scan report for 192.168.1.1
Host is up (0.001s latency).
MAC Address: AA:BB:CC:DD:EE:FF (Manufacturer)"""
            
            monitor._parse(new_output)
            
            devices = monitor.devices()
            assert len(devices) == 1
            assert devices[0].mac_address == 'aa:bb:cc:dd:ee:ff'

    def test_scan_method(self, mock_nmap_executable, sample_nmap_output):
        """Test the scan method integration."""
        monitor = NetworkMonitor(network='192.168.1.0/24', verbose=True)
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = sample_nmap_output
        mock_result.stderr = ""
        
        with patch('subprocess.run', return_value=mock_result), \
             patch('builtins.print') as mock_print:
            
            monitor.scan()
            
            # Verify verbose output was printed
            mock_print.assert_called_once_with(sample_nmap_output)
            
            # Verify devices were parsed
            devices = monitor.devices()
            assert len(devices) == 3

    def test_to_json(self, mock_nmap_executable, temp_output_file):
        """Test JSON export functionality."""
        with patch('simple_scanner.scanner.get_core_data_file') as mock_get_file:
            mock_get_file.return_value.exists.return_value = False
            monitor = NetworkMonitor(network='192.168.1.0/24', use_persistence=False)
        
        # Add a test device
        test_device = Device('aa:bb:cc:dd:ee:ff', '192.168.1.100')
        monitor._devices['aa:bb:cc:dd:ee:ff'] = test_device
        
        monitor.to_json(str(temp_output_file))
        
        # Verify file was created and contains expected data
        assert temp_output_file.exists()
        
        with open(temp_output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert len(data) == 1
        assert data[0]['mac_address'] == 'aa:bb:cc:dd:ee:ff'
        assert data[0]['ip_address'] == '192.168.1.100'

    def test_to_csv(self, mock_nmap_executable, tmp_path):
        """Test CSV export functionality."""
        with patch('simple_scanner.scanner.get_core_data_file') as mock_get_file:
            mock_get_file.return_value.exists.return_value = False
            monitor = NetworkMonitor(network='192.168.1.0/24', use_persistence=False)
        csv_file = tmp_path / "test_output.csv"
        
        # Add a test device
        test_device = Device('aa:bb:cc:dd:ee:ff', '192.168.1.100')
        monitor._devices['aa:bb:cc:dd:ee:ff'] = test_device
        
        monitor.to_csv(str(csv_file))
        
        # Verify file was created and contains expected data
        assert csv_file.exists()
        
        with open(csv_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 1
        assert rows[0]['mac_address'] == 'aa:bb:cc:dd:ee:ff'
        assert rows[0]['ip_address'] == '192.168.1.100'

    def test_load_existing_data_success(self, mock_nmap_executable, tmp_path):
        """Test loading existing device data from JSON file."""
        data_file = tmp_path / "existing_devices.json"
        
        # Create existing data file
        existing_data = [
            {
                'mac_address': 'aa:bb:cc:dd:ee:ff',
                'ip_address': '192.168.1.100',
                'date_added': '2023-01-01T10:00:00+00:00',
                'last_seen': '2023-01-01T11:00:00+00:00'
            }
        ]
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f)
        
        # Create monitor with existing data file
        with patch('simple_scanner.scanner.get_core_data_file', return_value=data_file):
            monitor = NetworkMonitor(network='192.168.1.0/24', use_persistence=True, verbose=True)
        
        # Verify device was loaded
        devices = monitor.devices()
        assert len(devices) == 1
        assert devices[0].mac_address == 'aa:bb:cc:dd:ee:ff'
        assert devices[0].ip_address == '192.168.1.100'
        assert devices[0].date_added.isoformat() == '2023-01-01T10:00:00+00:00'
        assert devices[0].last_seen.isoformat() == '2023-01-01T11:00:00+00:00'

    def test_load_existing_data_preserves_date_added(self, mock_nmap_executable, tmp_path, mock_datetime):
        """Test that existing devices preserve their original date_added."""
        data_file = tmp_path / "existing_devices.json"
        
        # Create existing data file with older date_added
        old_date = datetime.datetime(2023, 1, 1, 10, 0, 0, tzinfo=datetime.timezone.utc)
        existing_data = [
            {
                'mac_address': 'aa:bb:cc:dd:ee:ff',
                'ip_address': '192.168.1.100',
                'date_added': old_date.isoformat(),
                'last_seen': old_date.isoformat()
            }
        ]
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f)
        
        # Create monitor and simulate a scan finding the same device
        with patch('simple_scanner.scanner.get_core_data_file', return_value=data_file):
            monitor = NetworkMonitor(network='192.168.1.0/24', use_persistence=True)
        
        nmap_output = """Nmap scan report for 192.168.1.100
Host is up (0.001s latency).
MAC Address: AA:BB:CC:DD:EE:FF (Manufacturer)"""
        
        with patch('datetime.datetime') as mock_dt:
            mock_dt.now.return_value = mock_datetime  # Current time
            mock_dt.timezone = MagicMock()
            mock_dt.timezone.utc = mock_datetime.tzinfo
            mock_dt.fromisoformat.return_value = old_date  # For loading existing data
            
            monitor._parse(nmap_output)
        
        devices = monitor.devices()
        assert len(devices) == 1
        
        # Verify date_added is preserved (old), but last_seen is updated (new)
        device = devices[0]
        assert device.date_added == old_date  # Preserved
        # Note: last_seen will be updated to mock_datetime during _parse

    def test_load_existing_data_nonexistent_file(self, mock_nmap_executable, tmp_path):
        """Test handling of nonexistent data file."""
        data_file = tmp_path / "nonexistent.json"
        
        # Should not raise error, just start with empty devices
        with patch('simple_scanner.scanner.get_core_data_file', return_value=data_file):
            monitor = NetworkMonitor(network='192.168.1.0/24', use_persistence=True)
        
        devices = monitor.devices()
        assert len(devices) == 0

    def test_load_existing_data_invalid_json(self, mock_nmap_executable, tmp_path):
        """Test handling of invalid JSON in data file."""
        data_file = tmp_path / "invalid.json"
        
        # Create invalid JSON file
        with open(data_file, 'w', encoding='utf-8') as f:
            f.write("invalid json content")
        
        # Should not raise error, just start with empty devices and show warning
        with patch('simple_scanner.scanner.get_core_data_file', return_value=data_file):
            monitor = NetworkMonitor(network='192.168.1.0/24', use_persistence=True, verbose=True)
        
        devices = monitor.devices()
        assert len(devices) == 0

    def test_update_ip_address_for_existing_device(self, mock_nmap_executable, tmp_path, mock_datetime):
        """Test that existing devices get IP updated when it changes (DHCP)."""
        data_file = tmp_path / "devices.json"
        
        # Create existing data with old IP
        old_date = datetime.datetime(2023, 1, 1, 10, 0, 0, tzinfo=datetime.timezone.utc)
        existing_data = [
            {
                'mac_address': 'aa:bb:cc:dd:ee:ff',
                'ip_address': '192.168.1.100',  # Old IP
                'date_added': old_date.isoformat(),
                'last_seen': old_date.isoformat()
            }
        ]
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f)
        
        with patch('simple_scanner.scanner.get_core_data_file', return_value=data_file):
            monitor = NetworkMonitor(network='192.168.1.0/24', use_persistence=True)
        
        # Simulate scan finding same device with new IP
        nmap_output = """Nmap scan report for 192.168.1.150
Host is up (0.001s latency).
MAC Address: AA:BB:CC:DD:EE:FF (Manufacturer)"""
        
        with patch('datetime.datetime') as mock_dt:
            mock_dt.now.return_value = mock_datetime
            mock_dt.timezone = MagicMock()
            mock_dt.timezone.utc = mock_datetime.tzinfo
            mock_dt.fromisoformat.return_value = old_date
            
            monitor._parse(nmap_output)
        
        devices = monitor.devices()
        assert len(devices) == 1
        
        device = devices[0]
        assert device.mac_address == 'aa:bb:cc:dd:ee:ff'
        assert device.ip_address == '192.168.1.150'  # Updated IP
        assert device.date_added == old_date  # Preserved