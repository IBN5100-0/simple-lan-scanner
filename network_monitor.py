import subprocess
import datetime
import re
import socket
import ipaddress
import shutil
from typing import Dict, List, Optional
from device import Device


def autodetect_network() -> str:
    """Determine the local IPv4 address and assume a /24 network."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
    finally:
        s.close()
    net = ipaddress.IPv4Network(local_ip + '/24', strict=False)
    return str(net)

class NetworkMonitor:
    """Scans the network using nmap and tracks devices."""

    HOST_REGEX = re.compile(
        r"^Nmap scan report for (?:[\w\.\-]+ )?\(?(?P<ip>\d+\.\d+\.\d+\.\d+)\)?"
    )
    MAC_REGEX = re.compile(
        r"^MAC Address: (?P<mac>(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2})"
    )

    def __init__(
        self,
        network: Optional[str] = None,
        remove_stale: bool = False,
        verbose: bool = False,
    ) -> None:
        self.network = network or autodetect_network()
        self.remove_stale = remove_stale
        self.verbose = verbose
        self._devices: Dict[str, Device] = {}

        # Locate nmap executable
        self._nmap_path = shutil.which('nmap')
        if not self._nmap_path:
            raise RuntimeError(
                "nmap not found. Please install nmap and ensure it's in your PATH."
            )

    def _run_command(self) -> str:
        """Run nmap ping scan on the target network and return its output."""
        cmd = [self._nmap_path, '-sn', self.network]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Nmap scan failed: {result.stderr.strip()}")
        return result.stdout

    def _parse(self, raw: str) -> None:
        now = datetime.datetime.now(datetime.timezone.utc)
        seen_macs = set()
        lines = raw.splitlines()

        for i, line in enumerate(lines):
            host_match = self.HOST_REGEX.match(line)
            if not host_match:
                continue
            ip = host_match.group('ip')
            mac: Optional[str] = None

            # Look ahead for MAC Address line
            for j in range(i+1, min(i+5, len(lines))):
                mac_match = self.MAC_REGEX.match(lines[j])
                if mac_match:
                    mac = mac_match.group('mac').lower()
                    break

            if not mac:
                continue

            seen_macs.add(mac)
            if mac in self._devices:
                self._devices[mac].update_last_seen(now)
            else:
                self._devices[mac] = Device(mac, ip, now, now)

        if self.remove_stale:
            stale = [m for m in self._devices if m not in seen_macs]
            for m in stale:
                del self._devices[m]

    def scan(self) -> None:
        """Perform an nmap ping scan and update devices."""
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
        fieldnames = ['mac_address', 'ip_address', 'date_added', 'last_seen']
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for d in self.devices():
                writer.writerow(d.to_dict())

