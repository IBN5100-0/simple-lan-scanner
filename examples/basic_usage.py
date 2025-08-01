#!/usr/bin/env python3
"""
Basic usage example for Simple LAN Scanner.

This example demonstrates how to use the NetworkMonitor class
to scan your local network and display discovered devices.
"""

from simple_scanner import NetworkMonitor, Device
from datetime import datetime, timezone


def main():
    # Create a network monitor instance
    monitor = NetworkMonitor()
    
    print("Starting network scan...")
    print(f"Scanning network: {monitor.network}")
    print("-" * 80)
    
    # Perform a scan
    monitor.scan()
    
    # Get all discovered devices
    devices = monitor.devices()
    
    if not devices:
        print("No devices found on the network.")
        return
    
    print(f"Found {len(devices)} devices:\n")
    
    # Display devices in a formatted table
    print(f"{'MAC Address':<18} {'IP Address':<16} {'Hostname':<25} {'Manufacturer':<30}")
    print("-" * 90)
    
    for device in devices:
        # Check if device is online (seen within last 2 minutes)
        is_online = (datetime.now(timezone.utc) - device.last_seen).total_seconds() < 120
        status = "●" if is_online else "○"
        
        print(f"{status} {device.mac_address:<17} {device.ip_address:<15} "
              f"{device.hostname or '-':<25} {device.manufacturer or 'Unknown':<30}")
    
    # Count online devices
    online_count = sum(1 for d in devices 
                      if (datetime.now(timezone.utc) - d.last_seen).total_seconds() < 120)
    
    print(f"\nTotal devices: {len(devices)} ({online_count} online)")
    
    # Export results
    print("\nExporting results...")
    monitor.export_json("network_scan.json")
    monitor.export_csv("network_scan.csv")
    print("Results exported to network_scan.json and network_scan.csv")


if __name__ == "__main__":
    main()