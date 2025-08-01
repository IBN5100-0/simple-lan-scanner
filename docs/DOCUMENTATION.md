# Simple LAN Scanner v1.0.0 - Documentation

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/IBN5100-0/simple-lan-scanner/releases/tag/v1.0.0)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![nmap required](https://img.shields.io/badge/requires-nmap-orange.svg)](https://nmap.org/)

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
   - [Command Line Interface](#command-line-interface)
   - [Graphical User Interface](#graphical-user-interface)
   - [Python API](#python-api)
5. [Architecture](#architecture)
6. [Configuration](#configuration)
7. [Data Storage](#data-storage)
8. [Development](#development)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)
11. [Contributing](#contributing)
12. [License](#license)

## Overview

Simple LAN Scanner v1.0.0 is a comprehensive network discovery and monitoring tool that identifies active devices on your local network. Built with Python, it provides real-time network monitoring through both command-line and graphical interfaces, making it suitable for network administrators, security professionals, and home users.

The tool leverages the power of nmap for accurate network scanning while providing a user-friendly interface and persistent device tracking. It automatically detects your network configuration, tracks device history, and provides detailed information about each discovered device.

## Features

### Core Functionality

- **Automatic Network Detection**: Intelligently detects and selects the most appropriate local network
- **Device Discovery**: Uses nmap ping sweeps to discover all active devices on the network
- **MAC Address Resolution**: Identifies device manufacturers using OUI database
- **Persistent Device Tracking**: Maintains historical data for all discovered devices
- **Real-time Monitoring**: Continuous scanning with configurable intervals
- **Multiple Export Formats**: Export device data as JSON or CSV

### Advanced Features

- **Online Status Tracking**: Devices are marked as online if seen within the last 2 minutes
- **Search and Filtering**: Filter devices by MAC address, IP, hostname, or manufacturer
- **Cross-Platform Support**: Works on Windows, Linux, and macOS
- **Customizable Settings**: Configure scan intervals, network ranges, and export options
- **Notification System**: Get alerts for new devices or status changes (GUI only)
- **Context Menu Actions**: Quick access to copy device information (GUI only)

## Installation

### Prerequisites

1. **Python 3.7 or higher**
   ```bash
   python --version  # Verify Python installation
   ```

2. **nmap**
   - **Windows**: `winget install -e --id Insecure.Nmap`
   - **Ubuntu/Debian**: `sudo apt install nmap`
   - **macOS**: `brew install nmap`
   - **Other**: Download from [nmap.org](https://nmap.org/download.html)

### Install from Source

```bash
# Clone the repository
git clone https://github.com/IBN5100-0/simple-lan-scanner.git
cd simple-lan-scanner

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with CLI support
pip install -e .[cli]

# Or install with development dependencies
pip install -e .[dev]
```

### Install from PyPI

```bash
pip install simple-lan-scanner[cli]==1.0.0
```

## Usage

### Command Line Interface

The CLI provides comprehensive network scanning capabilities through the `lan-scan` command.

#### Basic Commands

1. **One-time Network Scan**
   ```bash
   # Quick scan with default settings
   lan-scan scan
   
   # Scan with specific output file
   lan-scan scan -o devices.json
   lan-scan scan -o devices.csv
   
   # Verbose mode for debugging
   lan-scan scan --verbose
   
   # Scan specific network
   lan-scan scan --network 192.168.1.0/24
   ```

2. **Continuous Monitoring**
   ```bash
   # Monitor with default 30-second interval
   lan-scan monitor
   
   # Custom interval (in seconds)
   lan-scan monitor --interval 60
   
   # Monitor with filters
   lan-scan monitor --online-only              # Show only online devices
   lan-scan monitor --search "router"          # Search for specific devices
   lan-scan monitor --online-only --search "xiaomi"  # Combine filters
   
   # Export while monitoring
   lan-scan monitor --json devices.json --csv devices.csv
   ```

3. **Launch GUI**
   ```bash
   lan-scan gui
   ```

#### CLI Output Format

The CLI displays devices in a clean, tabular format:

```
MAC Address       | IP Address      | Hostname                  | Manufacturer               | First Seen       | Last Seen
------------------------------------------------------------------------------------------------------------------------------------------------
XX:XX:XX:XX:XX:XX | 192.168.1.1     | router.local              | Netgear Inc.               | 2025-01-15 10:30 | 2025-01-15 14:45
YY:YY:YY:YY:YY:YY | 192.168.1.100   | laptop.local              | Apple Inc.                 | 2025-01-15 10:30 | 2025-01-15 14:45
```

- **Green text**: Device is online (last seen < 2 minutes ago)
- **Default text**: Device is offline

### Graphical User Interface

The GUI provides a professional, feature-rich interface for network monitoring.

#### Main Window Components

1. **Menu Bar**
   - **File Menu**
     - Export to JSON: Save device data in JSON format
     - Export to CSV: Save device data in CSV format
     - Settings: Open advanced configuration dialog
     - Exit: Close the application
   - **View Menu**
     - Refresh: Manually trigger a network scan
     - Show Details Panel: Toggle device details view
     - Always on Top: Keep window above other applications
   - **Help Menu**
     - Documentation: Open online documentation
     - About: Show application information

2. **Toolbar**
   - **Start/Stop Scanning**: Toggle continuous monitoring
   - **Scan Once**: Perform a single network scan
   - **Online Only**: Filter to show only online devices
   - **Search Box**: Real-time search across all device properties
   - **Interval Display**: Shows current scan interval

3. **Device List (TreeView)**
   - **Columns**:
     - Status: Visual indicator (●) - Green for online, Gray for offline
     - MAC Address: Hardware address of the device
     - IP Address: Current network address
     - Hostname: Device name (if available)
     - Manufacturer: Vendor identification from OUI database
     - First Seen: Initial discovery timestamp
     - Last Seen: Most recent detection timestamp
   - **Features**:
     - Click column headers to sort
     - Resizable columns
     - Multi-select support
     - Keyboard navigation

4. **Context Menu** (Right-click on device)
   - Copy MAC Address
   - Copy IP Address
   - Copy All Details
   - Show in Details Panel
   - Export Selected

5. **Status Bar**
   - Device count: "Devices: X (Y online)"
   - Current network: "Scanning: 192.168.1.0/24"
   - Last update time: "Updated: HH:MM:SS"
   - Scan status indicator

#### Settings Dialog

Comprehensive configuration options organized in tabs:

1. **General Tab**
   - Scan interval: 5-300 seconds
   - Auto-start scanning on launch
   - Start minimized to system tray
   - Check for updates

2. **Network Tab**
   - Network selection: Auto-detect or manual
   - Custom network range (CIDR notation)
   - Exclude IP ranges
   - Advanced nmap options

3. **Display Tab**
   - Theme selection
   - Font size adjustment
   - Date/time format
   - Color customization

4. **Notifications Tab**
   - New device alerts
   - Device online/offline notifications
   - Sound alerts
   - System tray notifications

5. **Export Tab**
   - Default export directory
   - Automatic export on scan
   - Export format preferences
   - Include offline devices

6. **Advanced Tab**
   - Remove stale devices after X days
   - Database maintenance
   - Debug logging
   - Reset to defaults

### Python API

Integrate network scanning into your own applications:

```python
from simple_scanner import NetworkMonitor
from simple_scanner.models import Device

# Initialize scanner
monitor = NetworkMonitor()

# Perform a single scan
monitor.scan()

# Get all devices
devices = monitor.devices()
for device in devices:
    print(f"{device.mac_address} - {device.ip_address} - {device.manufacturer}")

# Get online devices only
online_devices = monitor.get_online_devices()

# Search for specific devices
router = monitor.find_device_by_hostname("router")
apple_devices = monitor.find_devices_by_manufacturer("Apple")

# Export data
monitor.export_json("network_snapshot.json")
monitor.export_csv("network_snapshot.csv")

# Custom network range
monitor.scan(network="10.0.0.0/24")

# Continuous monitoring
import time
while True:
    monitor.scan()
    print(f"Found {len(monitor.get_online_devices())} online devices")
    time.sleep(60)
```

## Architecture

### Project Structure

```
simple-lan-scanner/
├── .github/                     # GitHub-specific files
│   ├── ISSUE_TEMPLATE/         # Issue templates
│   │   ├── bug_report.md       # Bug report template
│   │   └── feature_request.md  # Feature request template
│   ├── workflows/              # GitHub Actions
│   │   └── tests.yml           # Automated testing workflow
│   ├── CODEOWNERS              # Code ownership definitions
│   ├── FUNDING.yml             # Funding configuration
│   ├── SECURITY.md             # Security policy
│   └── pull_request_template.md # PR template
├── docs/                        # Documentation
│   ├── DOCUMENTATION.md         # Main documentation (this file)
│   └── README.md                # Documentation index
├── examples/                    # Usage examples
│   ├── README.md                # Examples overview
│   ├── basic_usage.py           # Basic scanning example
│   ├── continuous_monitoring.py # Monitoring example
│   └── advanced_filtering.py    # Filtering example
├── src/
│   └── simple_scanner/          # Main package
│       ├── __init__.py          # Package initialization
│       ├── __main__.py          # Entry point for python -m
│       ├── cli.py               # Click-based CLI implementation
│       ├── gui.py               # Tkinter GUI implementation
│       ├── models.py            # Device data model
│       ├── scanner.py           # Core scanning engine
│       └── oui.py               # MAC vendor lookup (future)
├── tests/                       # Test suite
│   ├── conftest.py              # Pytest configuration
│   ├── test_cli.py              # CLI tests
│   ├── test_gui.py              # GUI tests
│   ├── test_models.py           # Model tests
│   ├── test_scanner.py          # Scanner tests
│   ├── test_scanner_hostname_manufacturer.py  # Extended tests
│   └── test_models_comprehensive.py           # Comprehensive tests
├── CHANGELOG.md                 # Version history (v1.0.0)
├── CLAUDE.md                    # AI assistant instructions
├── CONTRIBUTING.md              # Contribution guidelines
├── LICENSE                      # MIT License
├── Makefile                     # Development shortcuts
├── README.md                    # Project overview
├── pyproject.toml               # Project configuration
├── pytest.ini                   # Pytest configuration
├── requirements.txt             # Basic dependencies
└── requirements-dev.txt         # Development dependencies
```

### Core Components

#### NetworkMonitor (`scanner.py`)

The heart of the application, responsible for:
- Executing nmap commands via subprocess
- Parsing scan results using regex patterns
- Managing the device inventory
- Handling persistence operations
- Network auto-detection logic

Key methods:
- `scan(network=None)`: Execute a network scan
- `devices()`: Get all discovered devices
- `get_online_devices()`: Filter for recently seen devices
- `export_json(filename)`: Export to JSON format
- `export_csv(filename)`: Export to CSV format

#### Device Model (`models.py`)

Data class representing a network device:
```python
@dataclass
class Device:
    mac_address: str           # Primary key
    ip_address: str
    hostname: Optional[str] = None
    manufacturer: Optional[str] = None
    date_added: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

Features:
- MAC address normalization
- JSON serialization/deserialization
- String representation for display
- Comparison operators for sorting

#### CLI Module (`cli.py`)

Built with Click framework, providing:
- Command parsing and validation
- Output formatting with color support
- Filter implementation
- Signal handling for graceful shutdown
- Progress indicators

#### GUI Module (`gui.py`)

Tkinter-based interface featuring:
- Modern, responsive design
- Real-time updates
- Advanced filtering
- Settings persistence
- Event-driven architecture

### Data Flow

1. **Scan Initiation**
   ```
   User Input → NetworkMonitor.scan() → subprocess.run(nmap)
   ```

2. **Result Processing**
   ```
   nmap output → regex parsing → Device objects → update inventory
   ```

3. **Data Persistence**
   ```
   Device list → JSON serialization → filesystem storage
   ```

4. **UI Updates**
   ```
   Device changes → event emission → UI refresh → user display
   ```

## Configuration

### Environment Variables

- `SIMPLE_SCANNER_CONFIG_DIR`: Override default config directory
- `SIMPLE_SCANNER_NETWORK`: Force specific network (e.g., "192.168.1.0/24")
- `SIMPLE_SCANNER_INTERVAL`: Default scan interval in seconds
- `SIMPLE_SCANNER_DEBUG`: Enable debug logging

### Configuration File

Settings are stored in JSON format:

**Location**:
- Windows: `%APPDATA%\simple-lan-scanner\settings.json`
- Linux/Mac: `~/.config/simple-lan-scanner/settings.json`

**Example Configuration**:
```json
{
  "scan_interval": 30,
  "network": "auto",
  "auto_start": true,
  "online_threshold": 120,
  "export_format": "json",
  "export_directory": "~/network-scans",
  "remove_stale_days": 30,
  "notifications": {
    "new_device": true,
    "device_online": false,
    "device_offline": false,
    "sound_enabled": true
  },
  "gui": {
    "theme": "default",
    "always_on_top": false,
    "start_minimized": false,
    "window_geometry": "1200x600+100+100"
  }
}
```

## Data Storage

### Device Database

**Location**:
- Windows: `%APPDATA%\simple-lan-scanner\devices.json`
- Linux/Mac: `~/.local/share/simple-lan-scanner/devices.json`

**Format**:
```json
[
  {
    "mac_address": "XX:XX:XX:XX:XX:XX",
    "ip_address": "192.168.1.1",
    "hostname": "router.local",
    "manufacturer": "Netgear Inc.",
    "date_added": "2025-01-15T10:30:00Z",
    "last_seen": "2025-01-15T14:45:00Z"
  }
]
```

### Export Formats

#### JSON Export
Complete device information with full timestamps and metadata.

#### CSV Export
Tabular format suitable for spreadsheet applications:
```csv
MAC Address,IP Address,Hostname,Manufacturer,First Seen,Last Seen
XX:XX:XX:XX:XX:XX,192.168.1.1,router.local,Netgear Inc.,2025-01-15 10:30,2025-01-15 14:45
```

## Development

### Setting Up Development Environment

```bash
# Clone and enter directory
git clone https://github.com/IBN5100-0/simple-lan-scanner.git
cd simple-lan-scanner

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Run with coverage
pytest --cov=simple_scanner --cov-report=html
```

### Makefile Commands

```bash
make help          # Show all available commands
make install       # Install package
make install-dev   # Install with development dependencies
make test          # Run test suite
make test-cov      # Run tests with coverage report
make lint          # Run code linters
make format        # Format code with black
make clean         # Clean build artifacts
make build         # Build distribution packages
make release       # Create a new release
make scan          # Quick test scan
make gui           # Launch GUI for testing
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints for function signatures
- Maximum line length: 88 characters (Black default)
- Docstrings for all public functions and classes

### Adding New Features

1. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Implement with tests**
   - Add unit tests in `tests/`
   - Update documentation
   - Add examples if applicable

3. **Run quality checks**
   ```bash
   make test
   make lint
   ```

4. **Submit pull request**
   - Clear description of changes
   - Reference any related issues
   - Include test results
   - Ensure compatibility with v1.0.0

## Testing

### Test Structure

```
tests/
├── conftest.py                 # Shared fixtures
├── test_cli.py                 # CLI command tests
├── test_gui.py                 # GUI functionality tests
├── test_models.py              # Data model tests
├── test_scanner.py             # Scanner logic tests
├── test_scanner_hostname_manufacturer.py  # Extended scanner tests
└── test_models_comprehensive.py           # Comprehensive model tests
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_cli.py

# Run specific test
pytest tests/test_cli.py::TestCLI::test_scan_command

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=simple_scanner --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=simple_scanner --cov-report=html
open htmlcov/index.html
```

### Test Categories

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete workflows
4. **Performance Tests**: Ensure acceptable performance

### Writing Tests

Example test structure:
```python
import pytest
from simple_scanner.models import Device

class TestDevice:
    def test_mac_normalization(self):
        """Test MAC address is normalized to lowercase."""
        device = Device("AA:BB:CC:DD:EE:FF", "192.168.1.1")
        assert device.mac_address == "aa:bb:cc:dd:ee:ff"
    
    def test_online_status(self):
        """Test online status calculation."""
        device = Device("aa:bb:cc:dd:ee:ff", "192.168.1.1")
        # Device is online if last seen within 120 seconds
        now = datetime.now(timezone.utc)
        assert (now - device.last_seen).total_seconds() < 120
```

## Troubleshooting

### Common Issues

#### 1. "nmap not found" Error
**Problem**: The nmap binary is not in your system PATH.

**Solution**:
```bash
# Verify nmap installation
nmap --version

# Add to PATH if needed
# Windows: Add nmap directory to System Environment Variables
# Linux/Mac: Add to ~/.bashrc or ~/.zshrc
export PATH=$PATH:/usr/local/bin
```

#### 2. No Devices Found
**Problem**: Scan completes but no devices are discovered.

**Possible causes**:
- Firewall blocking ICMP packets
- Wrong network range
- Insufficient permissions

**Solutions**:
```bash
# Test with manual nmap command
nmap -sn 192.168.1.0/24

# Run with sudo on Linux/Mac
sudo lan-scan scan

# Check firewall settings
# Windows: Windows Defender Firewall
# Linux: iptables or ufw
```

#### 3. Permission Denied Errors
**Problem**: Cannot write to configuration directory.

**Solution**:
```bash
# Check directory permissions
ls -la ~/.config/simple-lan-scanner/

# Create directory with correct permissions
mkdir -p ~/.config/simple-lan-scanner
chmod 755 ~/.config/simple-lan-scanner
```

#### 4. GUI Not Starting
**Problem**: GUI fails to launch or crashes immediately.

**Possible causes**:
- Missing Tkinter
- Display issues
- Configuration corruption

**Solutions**:
```bash
# Test Tkinter installation
python -c "import tkinter; tkinter.Tk()"

# Reset configuration
rm ~/.config/simple-lan-scanner/settings.json

# Run in debug mode
SIMPLE_SCANNER_DEBUG=1 lan-scan gui
```

#### 5. Slow Scan Performance
**Problem**: Scans take too long to complete.

**Solutions**:
- Reduce network range (use /24 instead of /16)
- Increase nmap timing template
- Check network congestion

### Debug Mode

Enable detailed logging:
```bash
# Linux/Mac
export SIMPLE_SCANNER_DEBUG=1
lan-scan scan --verbose

# Windows
set SIMPLE_SCANNER_DEBUG=1
lan-scan scan --verbose
```

### Reporting Issues

When reporting issues, include:
1. Operating system and version
2. Python version (`python --version`)
3. nmap version (`nmap --version`)
4. Complete error message
5. Steps to reproduce
6. Debug log output

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas for Contribution

1. **Features**
   - IPv6 support
   - SNMP integration
   - Web interface
   - Mobile app

2. **Improvements**
   - Performance optimization
   - UI/UX enhancements
   - Additional export formats
   - Internationalization

3. **Documentation**
   - Tutorials
   - Video guides
   - API examples
   - Translations

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [nmap](https://nmap.org/) - Network exploration tool
- [Click](https://click.palletsprojects.com/) - CLI framework
- [Tkinter](https://docs.python.org/3/library/tkinter.html) - GUI framework
- IEEE OUI database for MAC vendor identification

---

For more information, visit the [project repository](https://github.com/IBN5100-0/simple-lan-scanner).

## Version

This documentation is for Simple LAN Scanner v1.0.0, released on August 1, 2025.