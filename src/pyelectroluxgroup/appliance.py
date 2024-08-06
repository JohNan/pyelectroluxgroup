from typing import Any, Dict

from aiohttp.client_exceptions import ClientResponseError

from pyelectroluxgroup.auth import Auth


class Appliance:
    """Class representing an appliance."""

    def __init__(self, initial_data: Dict, auth: Auth):
        """Initialize the appliance."""
        self.auth = auth
        self.initial_data = initial_data
        self.info_data: dict[str, str] = {}
        self.capabilities_data: dict[str, Any] = {}
        self.state_data: dict[str, Any] = {}

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

    async def send_command(self, command: Dict):
        resp = await self.auth.request(
            "put", f"appliances/{self.id}/command", json=command
        )
        try:
            data = await resp.json()
            resp.raise_for_status()
        except ClientResponseError as e:
            print(data)
            raise e

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

        print(self.info_data)
        print(self.capabilities_data)
        print(self.state_data)
