import datetime
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Device:
    """Represents a network device discovered via nmap ping scan."""
    mac_address: str
    ip_address: str
    date_added: datetime.datetime = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    last_seen: datetime.datetime = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

    def __post_init__(self):
        """Normalize MAC address to lowercase."""
        self.mac_address = self.mac_address.lower()

    def update_last_seen(self, timestamp: Optional[datetime.datetime] = None) -> None:
        self.last_seen = timestamp or datetime.datetime.now(datetime.timezone.utc)
    
    def update_ip_address(self, ip_address: str) -> None:
        """Update the IP address (useful for DHCP changes)."""
        self.ip_address = ip_address

    def to_dict(self) -> dict:
        return {
            'mac_address': self.mac_address,
            'ip_address': self.ip_address,
            'date_added': self.date_added.isoformat(),
            'last_seen': self.last_seen.isoformat(),
        }

    def __str__(self) -> str:
        return (
            f"MAC: {self.mac_address} | IP: {self.ip_address} | "
            f"First Seen: {self.date_added.isoformat()} | Last Seen: {self.last_seen.isoformat()}"
        )