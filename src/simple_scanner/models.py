import datetime
from dataclasses import dataclass, field

@dataclass
class Device:
    """Represents a network device discovered via nmap ping scan."""
    mac_address: str
    ip_address: str
    hostname: str | None = None
    manufacturer: str | None = None
    date_added: datetime.datetime = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    last_seen: datetime.datetime = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

    def __post_init__(self):
        """Normalize MAC address to lowercase."""
        self.mac_address = self.mac_address.lower()

    def update_last_seen(self, timestamp: datetime.datetime | None = None) -> None:
        self.last_seen = timestamp or datetime.datetime.now(datetime.timezone.utc)
    
    def update_ip_address(self, ip_address: str) -> None:
        """Update the IP address (useful for DHCP changes)."""
        self.ip_address = ip_address
    
    def update_hostname(self, hostname: str | None) -> None:
        """Update the hostname."""
        self.hostname = hostname
    
    def update_manufacturer(self, manufacturer: str | None) -> None:
        """Update the manufacturer."""
        self.manufacturer = manufacturer

    def to_dict(self) -> dict:
        return {
            'mac_address': self.mac_address,
            'ip_address': self.ip_address,
            'hostname': self.hostname,
            'manufacturer': self.manufacturer,
            'date_added': self.date_added.isoformat(),
            'last_seen': self.last_seen.isoformat(),
        }

    def __str__(self) -> str:
        # Create a formatted table-like string with fixed widths
        mac_str = f"{self.mac_address:<17}"  # MAC addresses are 17 chars
        ip_str = f"{self.ip_address:<15}"    # IP addresses up to 15 chars
        
        # Truncate long values with ellipsis
        hostname = self.hostname or '-'
        if len(hostname) > 25:
            hostname = hostname[:22] + '...'
        hostname_str = f"{hostname:<25}"
        
        manufacturer = self.manufacturer or '-'
        if len(manufacturer) > 28:
            manufacturer = manufacturer[:25] + '...'
        manufacturer_str = f"{manufacturer:<28}"
        
        # Convert UTC to local time for display
        first_seen_local = self.date_added.replace(tzinfo=datetime.timezone.utc).astimezone()
        last_seen_local = self.last_seen.replace(tzinfo=datetime.timezone.utc).astimezone()
        first_seen_str = first_seen_local.strftime("%Y-%m-%d %H:%M")
        last_seen_str = last_seen_local.strftime("%Y-%m-%d %H:%M")
        
        return f"{mac_str} | {ip_str} | {hostname_str} | {manufacturer_str} | {first_seen_str} | {last_seen_str}"