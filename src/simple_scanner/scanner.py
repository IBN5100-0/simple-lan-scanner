import subprocess
import datetime
import re
import socket
import ipaddress
import shutil
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from .models import Device


def get_user_data_dir() -> Path:
    """Get the user data directory for storing persistent device data."""
    if os.name == 'nt':  # Windows
        data_dir = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming')) / 'simple-lan-scanner'
    else:  # Unix-like (Linux, macOS)
        data_dir = Path.home() / '.simple-lan-scanner'
    
    # Create directory if it doesn't exist
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_core_data_file() -> Path:
    """Get the path to the core persistent data file."""
    return get_user_data_dir() / 'devices.json'


def autodetect_network() -> str:
    """
    Return the most likely 'home‑LAN' /24 network, skipping
    VirtualBox host‑only (192.168.56.*) and link‑local ranges.
    """
    hostname = socket.gethostname()
    ips = {info[4][0] for info in socket.getaddrinfo(hostname, None, socket.AF_INET)}

    # ------------------------------------------------------------------ #
    # 1) throw away addresses we almost never want to scan automatically
    # ------------------------------------------------------------------ #
    def unwanted(ip: str) -> bool:
        return (
            ip.startswith("169.254.")            # Windows APIPA
            or ip.startswith("192.168.56.")      # VirtualBox host‑only
        )

    ips = [ip for ip in ips if not unwanted(ip)]
    if not ips:
        raise RuntimeError("Could not find a suitable IPv4 address")

    # ------------------------------------------------------------------ #
    # 2) preference scores → choose highest
    # ------------------------------------------------------------------ #
    def score(ip: str) -> int:
        if ip.startswith("192.168."):
            return 3
        if ip.startswith("172.") and 16 <= int(ip.split(".")[1]) <= 31:
            return 2
        if ip.startswith("10."):
            return 1
        return 0

    best_ip = max(ips, key=score)
    return str(ipaddress.ip_network(f"{best_ip}/24", strict=False))

class NetworkMonitor:
    """Scans the network using nmap and tracks devices."""
    
    # Constants
    MAC_LOOKAHEAD_LINES = 4  # How many lines to look ahead for MAC address
    NMAP_TIMEOUT_SECONDS = 300  # 5 minute timeout for nmap scans

    # Updated regex to capture hostname if present
    HOST_REGEX = re.compile(
        r"^Nmap scan report for (?:(?P<hostname>[\w.-]+) \()?(?P<ip>\d+\.\d+\.\d+\.\d+)\)?"
    )
    # Updated regex to capture MAC and manufacturer
    MAC_REGEX = re.compile(
        r"^MAC Address: (?P<mac>(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2})(?: \((?P<manufacturer>[^)]+)\))?"
    )

    def __init__(
        self,
        network: Optional[str] = None,
        remove_stale: bool = False,
        verbose: bool = False,
        use_persistence: bool = True,
    ) -> None:
        self.network = network or autodetect_network()
        self.remove_stale = remove_stale
        self.verbose = verbose
        self.use_persistence = use_persistence
        self._devices: Dict[str, Device] = {}

        # Locate nmap executable
        self._nmap_path = shutil.which('nmap')
        if not self._nmap_path:
            raise RuntimeError(
                "nmap not found. Please install nmap and ensure it's in your PATH."
            )
        
        # Load existing device data if persistence is enabled
        if self.use_persistence:
            self._load_existing_data()

    def _run_command(self) -> str:
        """Run nmap ping scan on the target network and return its output."""
        cmd = [self._nmap_path, '-sn', self.network]
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=self.NMAP_TIMEOUT_SECONDS,
                check=False
            )
        except subprocess.TimeoutExpired as e:
            raise RuntimeError(f"Nmap scan timed out after {self.NMAP_TIMEOUT_SECONDS} seconds") from e
        except FileNotFoundError as e:
            raise RuntimeError(f"Nmap executable not found: {self._nmap_path}") from e
        except PermissionError as e:
            raise RuntimeError(f"Permission denied running nmap: {self._nmap_path}") from e
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            raise RuntimeError(f"Nmap scan failed (exit code {result.returncode}): {error_msg}")
        return result.stdout

    def _load_existing_data(self) -> None:
        """Load existing device data from the core data file if it exists."""
        core_file = get_core_data_file()
        if not core_file.exists():
            return
        
        try:
            with open(core_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for device_data in data:
                mac = device_data['mac_address'].lower()
                ip = device_data['ip_address']
                hostname = device_data.get('hostname')  # May not exist in old data
                manufacturer = device_data.get('manufacturer')  # May not exist in old data
                date_added = datetime.datetime.fromisoformat(device_data['date_added'])
                last_seen = datetime.datetime.fromisoformat(device_data['last_seen'])
                
                self._devices[mac] = Device(
                    mac_address=mac,
                    ip_address=ip,
                    hostname=hostname,
                    manufacturer=manufacturer,
                    date_added=date_added,
                    last_seen=last_seen
                )
                
            if self.verbose:
                print(f"Loaded {len(self._devices)} existing devices from {core_file}")
                
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            if self.verbose:
                print(f"Warning: Could not load existing data from {core_file}: {e}")

    def _save_core_data(self) -> None:
        """Save current device data to the core data file."""
        if not self.use_persistence:
            return
            
        core_file = get_core_data_file()
        # Ensure parent directory exists
        core_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = [d.to_dict() for d in self.devices()]
        
        try:
            with open(core_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except (OSError, IOError) as e:
            if self.verbose:
                print(f"Warning: Could not save core data to {core_file}: {e}")

    def _parse(self, raw: str) -> None:
        now = datetime.datetime.now(datetime.timezone.utc)
        seen_macs = set()
        lines = raw.splitlines()

        for i, line in enumerate(lines):
            host_match = self.HOST_REGEX.match(line)
            if not host_match:
                continue
            ip = host_match.group('ip')
            hostname = host_match.group('hostname')  # May be None
            mac: Optional[str] = None
            manufacturer: Optional[str] = None

            # Look ahead for MAC Address line
            for j in range(i+1, min(i+1+self.MAC_LOOKAHEAD_LINES, len(lines))):
                mac_match = self.MAC_REGEX.match(lines[j])
                if mac_match:
                    mac = mac_match.group('mac').lower()
                    manufacturer = mac_match.group('manufacturer')  # May be None
                    break

            if not mac:
                continue

            seen_macs.add(mac)
            if mac in self._devices:
                # Update existing device - preserve original date_added
                self._devices[mac].update_last_seen(now)
                # Update IP in case it changed (DHCP)
                self._devices[mac].update_ip_address(ip)
                # Update hostname if found
                if hostname:
                    self._devices[mac].update_hostname(hostname)
                # Update manufacturer if found
                if manufacturer:
                    self._devices[mac].update_manufacturer(manufacturer)
            else:
                # New device - set both timestamps to now
                self._devices[mac] = Device(
                    mac_address=mac,
                    ip_address=ip,
                    hostname=hostname,
                    manufacturer=manufacturer,
                    date_added=now,
                    last_seen=now
                )

        if self.remove_stale:
            stale = [m for m in self._devices if m not in seen_macs]
            for m in stale:
                del self._devices[m]
        
        # Always update the core data file if persistence is enabled
        if self.use_persistence:
            self._save_core_data()

    def scan(self) -> None:
        """Perform a nmap ping scan and update devices."""
        raw = self._run_command()
        if self.verbose:
            print(raw)
        self._parse(raw)

    def devices(self) -> List[Device]:
        """Return list of tracked devices."""
        return list(self._devices.values())

    def to_json(self, path: str) -> None:
        import json
        data = [d.to_dict() for d in self.devices()]
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def to_csv(self, path: str) -> None:
        import csv
        fieldnames = ['mac_address', 'ip_address', 'hostname', 'manufacturer', 'date_added', 'last_seen']
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for d in self.devices():
                writer.writerow(d.to_dict())

