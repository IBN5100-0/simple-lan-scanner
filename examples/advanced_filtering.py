#!/usr/bin/env python3
"""
Advanced filtering example for Simple LAN Scanner.

This example demonstrates how to filter and search for specific
devices based on various criteria like manufacturer, IP range,
online status, etc.
"""

from simple_scanner import NetworkMonitor
from datetime import datetime, timezone, timedelta
import ipaddress


def filter_by_manufacturer(devices, manufacturers):
    """Filter devices by manufacturer names."""
    manufacturers_lower = [m.lower() for m in manufacturers]
    return [d for d in devices 
            if d.manufacturer and any(m in d.manufacturer.lower() 
                                    for m in manufacturers_lower)]


def filter_by_ip_range(devices, start_ip, end_ip):
    """Filter devices within a specific IP range."""
    start = ipaddress.ip_address(start_ip)
    end = ipaddress.ip_address(end_ip)
    
    filtered = []
    for device in devices:
        try:
            ip = ipaddress.ip_address(device.ip_address)
            if start <= ip <= end:
                filtered.append(device)
        except ValueError:
            continue
    return filtered


def filter_recently_added(devices, days=7):
    """Filter devices added within the last N days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    return [d for d in devices if d.date_added >= cutoff]


def main():
    # Create monitor and scan
    monitor = NetworkMonitor()
    print("Scanning network...")
    monitor.scan()
    
    all_devices = monitor.devices()
    print(f"\nTotal devices found: {len(all_devices)}\n")
    
    # Example 1: Filter by online status
    print("=" * 60)
    print("ONLINE DEVICES (seen in last 2 minutes):")
    print("=" * 60)
    
    now = datetime.now(timezone.utc)
    online_devices = [d for d in all_devices 
                     if (now - d.last_seen).total_seconds() < 120]
    
    for device in online_devices:
        print(f"• {device.ip_address:<15} {device.mac_address} "
              f"({device.manufacturer or 'Unknown'})")
    print(f"\nOnline: {len(online_devices)} devices")
    
    # Example 2: Filter by manufacturer
    print("\n" + "=" * 60)
    print("DEVICES BY MANUFACTURER:")
    print("=" * 60)
    
    # Search for specific manufacturers
    search_manufacturers = ["Apple", "Samsung", "Xiaomi"]
    for manufacturer in search_manufacturers:
        filtered = filter_by_manufacturer(all_devices, [manufacturer])
        if filtered:
            print(f"\n{manufacturer} devices:")
            for device in filtered:
                print(f"  • {device.ip_address:<15} {device.mac_address} "
                      f"({device.hostname or 'No hostname'})")
    
    # Example 3: Filter by IP range
    print("\n" + "=" * 60)
    print("DEVICES IN IP RANGE 192.168.1.100 - 192.168.1.150:")
    print("=" * 60)
    
    range_devices = filter_by_ip_range(all_devices, "192.168.1.100", "192.168.1.150")
    for device in sorted(range_devices, key=lambda x: ipaddress.ip_address(x.ip_address)):
        print(f"• {device.ip_address:<15} {device.mac_address} "
              f"({device.hostname or 'No hostname'})")
    
    # Example 4: Recently added devices
    print("\n" + "=" * 60)
    print("RECENTLY ADDED DEVICES (last 7 days):")
    print("=" * 60)
    
    recent_devices = filter_recently_added(all_devices, days=7)
    for device in sorted(recent_devices, key=lambda x: x.date_added, reverse=True):
        added_date = device.date_added.strftime("%Y-%m-%d %H:%M")
        print(f"• {device.ip_address:<15} {device.mac_address} "
              f"(Added: {added_date})")
    
    # Example 5: Devices with hostnames
    print("\n" + "=" * 60)
    print("DEVICES WITH HOSTNAMES:")
    print("=" * 60)
    
    named_devices = [d for d in all_devices if d.hostname]
    for device in sorted(named_devices, key=lambda x: x.hostname or ""):
        print(f"• {device.hostname:<30} {device.ip_address:<15} "
              f"{device.mac_address}")
    
    # Example 6: Unknown/unidentified devices
    print("\n" + "=" * 60)
    print("UNKNOWN DEVICES (no manufacturer info):")
    print("=" * 60)
    
    unknown_devices = [d for d in all_devices 
                      if not d.manufacturer or d.manufacturer == "Unknown"]
    for device in unknown_devices:
        print(f"• {device.ip_address:<15} {device.mac_address} "
              f"({device.hostname or 'No hostname'})")
    
    print(f"\nTotal unknown devices: {len(unknown_devices)}")


if __name__ == "__main__":
    main()