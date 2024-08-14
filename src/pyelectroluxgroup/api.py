import logging
from typing import List

from aiohttp import ClientSession

from pyelectroluxgroup.appliance import Appliance
from pyelectroluxgroup.auth import Auth
from pyelectroluxgroup.token_manager import TokenManager

_LOGGER = logging.getLogger(__name__)


class ElectroluxHubAPI:
    """Class to communicate with the ExampleHub API."""

    def __init__(self, session: ClientSession, token_manager: TokenManager):
        """Initialize the API and store the auth so we can make requests."""
        self.token_manager = token_manager
        if not self.token_manager.ensure_credentials():
            raise ValueError("Token manager is missing credentials")

        self.auth = Auth(
            session,
            "https://api.developer.electrolux.one/api/v1",
            token_manager.api_key,
            self.async_get_access_token,
        )

    async def async_get_access_token(self) -> str:
        if self.token_manager.is_token_valid():
            return self.token_manager.access_token

        try:
            _LOGGER.debug("Refreshing access token")
            response = await self.auth.request(
                "post",
                "token/refresh",
                json={"refreshToken": self.token_manager.refresh_token},
                skip_auth_headers=True,
            )

            response.raise_for_status()
        except Exception as e:
            raise ValueError(f"Failed to get access token: {e}")

        data = await response.json()
        self.token_manager.update(data["accessToken"], data["refreshToken"])

        return self.token_manager.access_token

    async def async_get_appliances(self) -> List[Appliance]:
        """Return the appliances."""
        resp = await self.auth.request("get", "appliances")
        resp.raise_for_status()
        return [
            Appliance(appliance_data, self.auth) for appliance_data in await resp.json()
        ]

    async def async_get_appliance(self, appliance_id) -> Appliance:
        """Return the appliance."""
        resp = await self.auth.request("get", f"appliances/{appliance_id}/info")
        resp.raise_for_status()
        return Appliance(await resp.json(), self.auth)
