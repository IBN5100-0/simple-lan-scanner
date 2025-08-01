# Simple LAN Scanner Examples

This directory contains example scripts demonstrating various use cases for Simple LAN Scanner.

## Available Examples

### 1. [Basic Usage](basic_usage.py)
Simple example showing how to:
- Perform a network scan
- Display discovered devices
- Check online status
- Export results to JSON/CSV

```bash
python examples/basic_usage.py
```

### 2. [Continuous Monitoring](continuous_monitoring.py)
Advanced example demonstrating:
- Continuous network monitoring
- Device change detection (new devices, offline devices)
- IP address change tracking
- Real-time status updates

```bash
python examples/continuous_monitoring.py
```

### 3. [Advanced Filtering](advanced_filtering.py)
Comprehensive filtering example showing:
- Filter by online status
- Filter by manufacturer
- Filter by IP range
- Find recently added devices
- Identify devices with/without hostnames
- Find unknown devices

```bash
python examples/advanced_filtering.py
```

## Running the Examples

1. Make sure Simple LAN Scanner is installed:
   ```bash
   pip install -e .[cli]
   ```

2. Navigate to the examples directory:
   ```bash
   cd examples
   ```

3. Run any example:
   ```bash
   python basic_usage.py
   ```

## Creating Your Own Scripts

These examples demonstrate the Python API usage. You can use them as templates for your own scripts. The main components are:

```python
from simple_scanner import NetworkMonitor, Device

# Create monitor
monitor = NetworkMonitor()

# Scan network
monitor.scan()

# Get devices
devices = monitor.devices()

# Filter and process as needed
online_devices = [d for d in devices if is_online(d)]
```

## Notes

- Examples require nmap to be installed and in PATH
- Some examples may require administrator/root privileges on certain systems
- Modify the scripts to suit your specific network configuration