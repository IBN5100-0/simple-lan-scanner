# Simple LAN Scanner

[![CI](https://github.com/IBN5100-0/simple-lan-scanner/actions/workflows/tests.yml/badge.svg)](https://github.com/IBN5100-0/simple-lan-scanner/actions/workflows/tests.yml)
[![PyPI](https://img.shields.io/pypi/v/simple-lan-scanner.svg)](https://pypi.org/project/simple-lan-scanner/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Requires nmap](https://img.shields.io/badge/requires-nmap-orange.svg)](https://nmap.org/)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen)](docs/DOCUMENTATION.md)

> 🔍 A powerful yet simple network scanner for discovering devices on your local network

<p align="center">
  <img src="https://via.placeholder.com/600x400/1a1a1a/00ff00?text=Simple+LAN+Scanner" alt="Simple LAN Scanner Demo" />
</p>

## ✨ Features

- 🚀 **Fast Network Discovery** - Leverages nmap for efficient ping sweeps
- 💻 **Dual Interface** - Both CLI and GUI options available
- 📊 **Device Tracking** - Persistent storage with historical data
- 🔍 **Smart Filtering** - Search by MAC, IP, hostname, or manufacturer
- 📁 **Multiple Export Formats** - JSON and CSV support
- 🎯 **Auto Network Detection** - Intelligently finds your local network
- 🔔 **Real-time Monitoring** - Continuous scanning with customizable intervals
- 🎨 **Modern GUI** - Clean, intuitive interface with online/offline status

## 🚀 Quick Start

### Installation

```bash
# From PyPI (recommended)
pip install simple-lan-scanner[cli]

# From source
git clone https://github.com/IBN5100-0/simple-lan-scanner.git
cd simple-lan-scanner
pip install -e .[cli]
```

### Requirements

- Python 3.8+
- [nmap](https://nmap.org/download.html) installed and in PATH

### Basic Usage

```bash
# Quick network scan
lan-scan scan

# Launch GUI
lan-scan gui

# Monitor network (updates every 30s)
lan-scan monitor

# Export results
lan-scan scan -o devices.json
```

## 📸 Screenshots

### CLI Interface
```
MAC Address       | IP Address      | Hostname                  | Manufacturer               | First Seen       | Last Seen
------------------------------------------------------------------------------------------------------------------------------------------------
XX:XX:XX:XX:XX:XX | 192.168.1.1     | router.local              | Netgear Inc.               | 2025-01-15 10:30 | 2025-01-15 14:45
YY:YY:YY:YY:YY:YY | 192.168.1.100   | laptop.local              | Apple Inc.                 | 2025-01-15 10:30 | 2025-01-15 14:45
```
- 🟢 Green = Online (seen < 2 minutes ago)
- ⚪ Default = Offline

### GUI Features
- Real-time device monitoring
- Search and filter capabilities
- Export to JSON/CSV
- Detailed device information
- Context menu for quick actions

## 🛠️ Advanced Usage

### CLI Commands

```bash
# Scan specific network
lan-scan scan --network 192.168.1.0/24

# Monitor with filters
lan-scan monitor --online-only --search "apple"

# Custom scan interval
lan-scan monitor --interval 60 --json devices.json
```

### Python API

```python
from simple_scanner import NetworkMonitor

# Initialize scanner
monitor = NetworkMonitor()

# Scan network
monitor.scan()

# Get devices
devices = monitor.devices()
for device in devices:
    print(f"{device.mac_address} - {device.ip_address}")

# Export results
monitor.export_json("scan_results.json")
```

## 📚 Documentation

- 📖 **[Full Documentation](docs/DOCUMENTATION.md)** - Complete usage guide
- 💡 **[Examples](examples/)** - Code examples and use cases
- 🤝 **[Contributing](CONTRIBUTING.md)** - How to contribute
- 📝 **[Changelog](CHANGELOG.md)** - Version history
- 🔒 **[Security](https://github.com/IBN5100-0/simple-lan-scanner/security/policy)** - Security policy

## 🏗️ Project Structure

```
simple-lan-scanner/
├── src/simple_scanner/    # Core package
├── tests/                 # Test suite
├── docs/                  # Documentation
├── examples/              # Usage examples
└── .github/               # GitHub configuration
```

## 🧪 Development

```bash
# Setup development environment
git clone https://github.com/IBN5100-0/simple-lan-scanner.git
cd simple-lan-scanner
pip install -e .[dev]

# Run tests
pytest

# Run with coverage
pytest --cov=simple_scanner

# Format code
black src/ tests/
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Areas for Contribution
- IPv6 support
- Web interface
- Additional export formats
- Performance optimizations
- Documentation improvements

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [nmap](https://nmap.org/) - The foundation of our network scanning
- [Click](https://click.palletsprojects.com/) - CLI framework
- [Tkinter](https://docs.python.org/3/library/tkinter.html) - GUI framework

## 🔗 Links

- [PyPI Package](https://pypi.org/project/simple-lan-scanner/)
- [GitHub Repository](https://github.com/IBN5100-0/simple-lan-scanner)
- [Issue Tracker](https://github.com/IBN5100-0/simple-lan-scanner/issues)
- [Discussions](https://github.com/IBN5100-0/simple-lan-scanner/discussions)

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/IBN5100-0">IBN5100-0</a>
</p>