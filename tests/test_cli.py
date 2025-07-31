"""Tests for the CLI functionality."""

import pytest
import json
import csv
from pathlib import Path
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from simple_scanner.cli import app
from simple_scanner.models import Device


class TestCLI:
    """Test cases for CLI commands."""

    def test_app_help(self):
        """Test that the main app shows help correctly."""
        runner = CliRunner()
        result = runner.invoke(app, ['--help'])
        
        assert result.exit_code == 0
        assert 'simple-lan-scanner' in result.output
        assert 'scan' in result.output
        assert 'monitor' in result.output
        assert 'gui' in result.output

    def test_scan_command_help(self):
        """Test scan command help."""
        runner = CliRunner()
        result = runner.invoke(app, ['scan', '--help'])
        
        assert result.exit_code == 0
        assert 'Scan once and write JSON/CSV' in result.output
        assert '--out' in result.output
        assert '--network' in result.output
        assert '--verbose' in result.output

    def test_monitor_command_help(self):
        """Test monitor command help."""
        runner = CliRunner()
        result = runner.invoke(app, ['monitor', '--help'])
        
        assert result.exit_code == 0
        assert 'Continuous scan every N seconds' in result.output
        assert '--interval' in result.output

    def test_gui_command_help(self):
        """Test GUI command help."""
        runner = CliRunner()
        result = runner.invoke(app, ['gui', '--help'])
        
        assert result.exit_code == 0
        assert 'Launch the GUI application' in result.output

    @patch('simple_scanner.cli.NetworkMonitor')
    def test_scan_command_json_output(self, mock_monitor_class, tmp_path):
        """Test scan command with JSON output."""
        # Setup mock
        mock_monitor = MagicMock()
        mock_monitor_class.return_value = mock_monitor
        
        runner = CliRunner()
        output_file = tmp_path / "test_output.json"
        
        result = runner.invoke(app, ['scan', '--out', str(output_file)])
        
        assert result.exit_code == 0
        assert 'wrote' in result.output
        
        # Verify NetworkMonitor was called correctly
        mock_monitor_class.assert_called_once_with(
            network=None, 
            verbose=False, 
            remove_stale=False
        )
        mock_monitor.scan.assert_called_once()
        mock_monitor.to_json.assert_called_once()

    @patch('simple_scanner.cli.NetworkMonitor')
    def test_scan_command_csv_output(self, mock_monitor_class, tmp_path):
        """Test scan command with CSV output."""
        # Setup mock
        mock_monitor = MagicMock()
        mock_monitor_class.return_value = mock_monitor
        
        runner = CliRunner()
        output_file = tmp_path / "test_output.csv"
        
        result = runner.invoke(app, ['scan', '--out', str(output_file)])
        
        assert result.exit_code == 0
        assert 'wrote' in result.output
        
        # Verify NetworkMonitor was called correctly
        mock_monitor_class.assert_called_once_with(
            network=None, 
            verbose=False, 
            remove_stale=False
        )
        mock_monitor.scan.assert_called_once()
        mock_monitor.to_csv.assert_called_once()

    @patch('simple_scanner.cli.NetworkMonitor')
    def test_scan_command_with_options(self, mock_monitor_class):
        """Test scan command with various options."""
        # Setup mock
        mock_monitor = MagicMock()
        mock_monitor_class.return_value = mock_monitor
        
        runner = CliRunner()
        
        result = runner.invoke(app, [
            'scan', 
            '--network', '10.0.0.0/24',
            '--verbose',
            '--remove-stale'
        ])
        
        assert result.exit_code == 0
        
        # Verify NetworkMonitor was called with correct options
        mock_monitor_class.assert_called_once_with(
            network='10.0.0.0/24', 
            verbose=True, 
            remove_stale=True
        )

    def test_scan_command_invalid_output_extension(self):
        """Test scan command with invalid output file extension."""
        runner = CliRunner()
        
        result = runner.invoke(app, ['scan', '--out', 'invalid.txt'])
        
        assert result.exit_code == 1
        assert '--out must end with .json or .csv' in result.output

    @patch('simple_scanner.cli.NetworkMonitor')
    @patch('simple_scanner.cli.time.sleep')
    def test_monitor_command(self, mock_sleep, mock_monitor_class):
        """Test monitor command basic functionality."""
        # Setup mock
        mock_monitor = MagicMock()
        mock_monitor.network = '192.168.1.0/24'
        mock_monitor.devices.return_value = []
        mock_monitor_class.return_value = mock_monitor
        
        # Make sleep raise KeyboardInterrupt to exit the loop
        mock_sleep.side_effect = KeyboardInterrupt()
        
        runner = CliRunner()
        
        result = runner.invoke(app, ['monitor', '--interval', '5'])
        
        assert result.exit_code == 0
        assert 'Scanning 192.168.1.0/24 every 5s' in result.output
        assert 'Stopped by user' in result.output
        
        # Verify NetworkMonitor was called correctly
        mock_monitor_class.assert_called_once_with(
            network=None, 
            verbose=False, 
            remove_stale=False
        )
        mock_monitor.scan.assert_called()

    @patch('simple_scanner.cli.NetworkMonitor')
    @patch('simple_scanner.cli.time.sleep')
    def test_monitor_command_with_custom_paths(self, mock_sleep, mock_monitor_class):
        """Test monitor command with custom JSON and CSV paths."""
        # Setup mock
        mock_monitor = MagicMock()
        mock_monitor.network = '192.168.1.0/24'
        mock_monitor.devices.return_value = []
        mock_monitor_class.return_value = mock_monitor
        
        # Make sleep raise KeyboardInterrupt after first iteration
        mock_sleep.side_effect = KeyboardInterrupt()
        
        runner = CliRunner()
        
        result = runner.invoke(app, [
            'monitor', 
            '--json', 'custom.json',
            '--csv', 'custom.csv',
            '--verbose'
        ])
        
        assert result.exit_code == 0
        
        # Verify file operations were called
        mock_monitor.to_json.assert_called_with('custom.json')
        mock_monitor.to_csv.assert_called_with('custom.csv')

    @patch('simple_scanner.cli.NetworkMonitor')
    @patch('simple_scanner.cli.time.sleep')
    def test_monitor_command_exception_handling(self, mock_sleep, mock_monitor_class):
        """Test monitor command exception handling."""
        # Setup mock to raise exception
        mock_monitor = MagicMock()
        mock_monitor.scan.side_effect = RuntimeError("Scan failed")
        mock_monitor_class.return_value = mock_monitor
        
        runner = CliRunner()
        
        result = runner.invoke(app, ['monitor'])
        
        assert result.exit_code == 1
        assert 'Error: Scan failed' in result.output

    @patch('simple_scanner.gui.main')
    def test_gui_command_success(self, mock_gui_main):
        """Test GUI command successful launch."""
        runner = CliRunner()
        
        result = runner.invoke(app, ['gui'])
        
        assert result.exit_code == 0
        mock_gui_main.assert_called_once()

    def test_gui_command_import_error(self):
        """Test GUI command when GUI dependencies are not available."""
        runner = CliRunner()
        
        with patch('simple_scanner.gui.main', side_effect=ImportError()):
            result = runner.invoke(app, ['gui'])
            
            assert result.exit_code == 1
            assert 'GUI dependencies not available' in result.output

    @patch('simple_scanner.gui.main')
    def test_gui_command_runtime_error(self, mock_gui_main):
        """Test GUI command when GUI raises runtime error."""
        mock_gui_main.side_effect = RuntimeError("GUI initialization failed")
        
        runner = CliRunner()
        
        result = runner.invoke(app, ['gui'])
        
        assert result.exit_code == 1
        assert 'GUI Error: GUI initialization failed' in result.output

    @patch('simple_scanner.cli.NetworkMonitor')
    def test_scan_command_default_timestamped_output(self, mock_monitor_class):
        """Test scan command creates timestamped output when no --out specified."""
        # Setup mock
        mock_monitor = MagicMock()
        mock_monitor_class.return_value = mock_monitor
        
        runner = CliRunner()
        
        with patch('simple_scanner.cli.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = '20230101_120000'
            
            result = runner.invoke(app, ['scan'])
            
            assert result.exit_code == 0
            assert 'devices_20230101_120000.json' in result.output

    def test_monitor_interval_validation(self):
        """Test that monitor command validates interval range."""
        runner = CliRunner()
        
        # Test interval too low
        result = runner.invoke(app, ['monitor', '--interval', '1'])
        assert result.exit_code != 0
        
        # Test interval too high
        result = runner.invoke(app, ['monitor', '--interval', '4000'])
        assert result.exit_code != 0
        
        # Test valid interval
        with patch('simple_scanner.cli.NetworkMonitor'), \
             patch('simple_scanner.cli.time.sleep', side_effect=KeyboardInterrupt()):
            
            result = runner.invoke(app, ['monitor', '--interval', '30'])
            assert result.exit_code == 0