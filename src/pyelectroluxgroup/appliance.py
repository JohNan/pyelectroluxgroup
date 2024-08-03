from typing import Dict

from pyelectroluxgroup.auth import Auth


class Appliance:
    """Class representing an appliance."""

    def __init__(self, raw_data: Dict, auth: Auth):
        """Initialize the appliance."""
        self.auth = auth
        self.raw_data = raw_data

    @property
    def id(self) -> int:
        """Return the appliance ID."""
        return self.raw_data["applianceId"]

    @property
    def name(self) -> str:
        """Return the appliance name."""
        return self.raw_data["applianceName"]

    async def async_update(self):
        """Update the light data."""
        resp = await self.auth.request("get", f"appliances/{self.id}")
        resp.raise_for_status()
        self.raw_data = await resp.json()
