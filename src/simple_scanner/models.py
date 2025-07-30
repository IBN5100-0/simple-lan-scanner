import datetime
from typing import Optional

class Device:
    """Represents a network device discovered via nmap ping scan."""
    __slots__ = ("_mac_address", "_ip_address", "_date_added", "_last_seen")

    def __init__(
        self,
        mac_address: str,
        ip_address: str,
        date_added: Optional[datetime.datetime] = None,
        last_seen: Optional[datetime.datetime] = None,
    ) -> None:
        now = datetime.datetime.now(datetime.timezone.utc)
        self._mac_address = mac_address.lower()
        self._ip_address = ip_address
        self._date_added = date_added or now
        self._last_seen = last_seen or now

    @property
    def mac_address(self) -> str:
        return self._mac_address

    @property
    def ip_address(self) -> str:
        return self._ip_address

    @property
    def date_added(self) -> str:
        return self._date_added.isoformat()

    @property
    def last_seen(self) -> str:
        return self._last_seen.isoformat()

    def update_last_seen(self, timestamp: Optional[datetime.datetime] = None) -> None:
        self._last_seen = timestamp or datetime.datetime.now(datetime.timezone.utc)

    def to_dict(self) -> dict:
        return {
            'mac_address': self.mac_address,
            'ip_address': self.ip_address,
            'date_added': self.date_added,
            'last_seen': self.last_seen,
        }

    def __str__(self) -> str:
        return (
            f"MAC: {self.mac_address} | IP: {self.ip_address} | "
            f"First Seen: {self.date_added} | Last Seen: {self.last_seen}"
        )