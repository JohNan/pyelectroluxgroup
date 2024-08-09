import logging
from typing import Any, Dict

from aiohttp.client_exceptions import ClientResponseError

from pyelectroluxgroup.auth import Auth

_LOGGER = logging.getLogger(__name__)


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
    def type(self) -> str:
        """Return the appliance name."""
        return self.initial_data["applianceType"]

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
    def status(self) -> str:
        """Return the appliance status"""
        return self.state_data["status"]

    @property
    def connection_state(self) -> str:
        """Return the appliance connection_state"""
        return self.state_data["connectionState"]

    @property
    def state(self) -> dict:
        """Return the appliance reported state"""
        return self.state_data["properties"]["reported"]

    @property
    def capabilities(self) -> dict:
        """Return the appliance capabilities"""
        return self.capabilities_data

    async def send_command(self, command: Dict):
        _LOGGER.info(f"Command '{command}' sent to appliance {self.id}")
        resp = await self.auth.request(
            "put", f"appliances/{self.id}/command", json=command
        )
        try:
            data = await resp.json()
            _LOGGER.info(f"Response from appliance {self.id}: {data}")
            resp.raise_for_status()
        except ClientResponseError as e:
            _LOGGER.error(f"Error sending command '{command}' to appliance {self.id}")
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
        _LOGGER.debug(f"Appliance info {self.info_data}")
        _LOGGER.debug(f"Appliance state {self.state_data}")
        _LOGGER.debug(f"Appliance capabilities {self.capabilities_data}")
