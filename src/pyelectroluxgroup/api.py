import json
import logging
from typing import Any, AsyncGenerator, List

from aiohttp import ClientSession
from aiohttp_sse_client.client import EventSource

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

    async def watch_appliances(self) -> AsyncGenerator[dict[str, Any], None]:
        """Listen to the live stream for changes."""
        import asyncio

        import aiohttp

        while True:
            try:
                resp = await self.auth.request("get", "configurations/livestream")
                resp.raise_for_status()
                stream_data = await resp.json()
                stream_url = stream_data["url"]

                headers = await self.auth.get_headers()
                async with EventSource(
                    stream_url, session=self.auth.session, headers=headers
                ) as event_source:
                    async for event in event_source:
                        if not event.data:
                            continue

                        try:
                            data = json.loads(event.data)
                        except json.JSONDecodeError:
                            _LOGGER.warning(
                                f"Failed to decode stream event: {event.data}"
                            )
                            continue

                        if (
                            "applianceId" in data
                            and "property" in data
                            and "value" in data
                        ):
                            yield data
            except aiohttp.ClientResponseError as e:
                if e.status in [401, 403]:
                    _LOGGER.warning(
                        "Live stream auth error, token will be refreshed on next attempt"
                    )
                else:
                    _LOGGER.error(f"Live stream request error: {e}")
            except (aiohttp.ClientError, ConnectionError, asyncio.TimeoutError) as e:
                _LOGGER.error(f"Live stream connection error: {e}")
            except Exception as e:
                if type(e).__name__ == "BreakLoopException":
                    raise e
                _LOGGER.error(f"Live stream unexpected error: {e}")

            _LOGGER.info("Reconnecting to live stream in 5 seconds...")
            await asyncio.sleep(5)
