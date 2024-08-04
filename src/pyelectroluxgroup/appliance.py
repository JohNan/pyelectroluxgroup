from typing import Dict

from pyelectroluxgroup.auth import Auth


class Appliance:
    """Class representing an appliance."""

    def __init__(self, initial_data: Dict, auth: Auth):
        """Initialize the appliance."""
        self.auth = auth
        self.initial_data = initial_data
        self.info_data = {}
        self.capabilities_data = {}
        self.state_data = {}

    @property
    def id(self) -> int:
        """Return the appliance ID."""
        return self.initial_data["applianceId"]

    @property
    def name(self) -> str:
        """Return the appliance name."""
        return self.initial_data["applianceName"]

    @property
    def serial_number(self) -> str:
        """Return the appliance serial number."""
        return self.info_data["serialNumber"]

    @property
    def brand(self) -> str:
        """Return the appliance brand."""
        return self.info_data["brand"]

    @property
    def model(self) -> str:
        """Return the appliance model"""
        return self.info_data["model"]

    @property
    def pnc(self) -> str:
        """Return the appliance pnc"""
        return self.info_data["pnc"]

    @property
    def device_type(self) -> str:
        """Return the appliance pnc"""
        return self.info_data["deviceType"]

    @property
    def state(self) -> dict:
        """Return the appliance reported state"""
        return self.state_data["properties"]["reported"]

    async def async_update(self):
        """Update the appliance data."""
        if not self.info_data:
            resp = await self.auth.request("get", f"appliances/{self.id}/info")
            resp.raise_for_status()
            data = await resp.json()
            self.info_data = data["applianceInfo"]
            self.capabilities_data = data["capabilities"]

        resp = await self.auth.request("get", f"appliances/{self.id}/state")
        resp.raise_for_status()
        self.state_data = await resp.json()
