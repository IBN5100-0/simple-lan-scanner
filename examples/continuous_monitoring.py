#!/usr/bin/env python3
"""
Continuous monitoring example for Simple LAN Scanner.

This example shows how to continuously monitor your network
and get notifications when devices come online or go offline.
"""

import time
import signal
import sys
from datetime import datetime, timezone
from simple_scanner import NetworkMonitor


class NetworkWatcher:
    def __init__(self):
        self.monitor = NetworkMonitor()
        self.previous_devices = {}
        self.running = True
        
    def signal_handler(self, sig, frame):
        """Handle Ctrl+C gracefully."""
        print("\n\nStopping network monitoring...")
        self.running = False
        sys.exit(0)
        
    def check_device_changes(self, current_devices):
        """Check for new devices or status changes."""
        current_macs = {d.mac_address: d for d in current_devices}
        
        # Check for new devices
        for mac, device in current_macs.items():
            if mac not in self.previous_devices:
                print(f"🆕 NEW DEVICE: {device.mac_address} ({device.ip_address}) "
                      f"- {device.manufacturer or 'Unknown'}")
                
        # Check for devices that went offline
        for mac, device in self.previous_devices.items():
            if mac not in current_macs:
                print(f"❌ DEVICE OFFLINE: {device.mac_address} ({device.ip_address}) "
                      f"- {device.manufacturer or 'Unknown'}")
                
        # Check for IP changes
        for mac, device in current_macs.items():
            if mac in self.previous_devices:
                old_device = self.previous_devices[mac]
                if old_device.ip_address != device.ip_address:
                    print(f"🔄 IP CHANGED: {device.mac_address} "
                          f"from {old_device.ip_address} to {device.ip_address}")
                    
        self.previous_devices = current_macs
        
    def run(self, interval=30):
        """Run continuous monitoring."""
        signal.signal(signal.SIGINT, self.signal_handler)
        
        print(f"Starting continuous network monitoring...")
        print(f"Scanning {self.monitor.network} every {interval} seconds")
        print("Press Ctrl+C to stop\n")
        
        while self.running:
            # Perform scan
            self.monitor.scan()
            devices = self.monitor.devices()
            
            # Get online devices
            now = datetime.now(timezone.utc)
            online_devices = [d for d in devices 
                            if (now - d.last_seen).total_seconds() < 120]
            
            # Display summary
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{timestamp}] Network Status: "
                  f"{len(online_devices)} devices online (Total: {len(devices)})")
            
            # Check for changes
            self.check_device_changes(online_devices)
            
            # Display current online devices
            if online_devices:
                print("\nCurrently online:")
                for device in sorted(online_devices, key=lambda x: x.ip_address):
                    hostname = device.hostname or "-"
                    manufacturer = device.manufacturer or "Unknown"
                    print(f"  • {device.ip_address:<15} {device.mac_address} "
                          f"({hostname}, {manufacturer})")
            
            # Wait for next scan
            if self.running:
                print(f"\nNext scan in {interval} seconds...", end='', flush=True)
                time.sleep(interval)


def main():
    # Create and run the network watcher
    watcher = NetworkWatcher()
    
    # Run with 30-second intervals (customize as needed)
    watcher.run(interval=30)


if __name__ == "__main__":
    main()