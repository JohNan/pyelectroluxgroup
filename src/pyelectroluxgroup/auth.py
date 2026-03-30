import logging
from typing import Callable

from aiohttp import ClientResponse, ClientSession

_LOGGER = logging.getLogger(__name__)


class Auth:
    """Class to make authenticated requests."""

    def __init__(
        self,
        session: ClientSession,
        host: str,
        api_key: str | None,
        async_get_access_token: Callable,
    ):
        """Initialize the auth."""
        import asyncio

        self.session = session
        self.host = host
        self.api_key = api_key
        self.async_get_access_token = async_get_access_token
        self._request_semaphore: asyncio.Semaphore | None = None

    async def get_headers(self) -> dict[str, str]:
        """Get the authentication headers."""
        headers = {}
        if self.api_key:
            headers["x-api-key"] = self.api_key

        try:
            access_token = await self.async_get_access_token()
            headers["authorization"] = f"Bearer {access_token}"
        except Exception as e:
            _LOGGER.error(f"Failed to get access token: {e}")
            raise e

        return headers

    async def request(self, method: str, path: str, **kwargs) -> ClientResponse:
        """Make a request."""
        import asyncio

        if self._request_semaphore is None:
            self._request_semaphore = asyncio.Semaphore(5)

        json = kwargs.get("json", None)
        headers = kwargs.get("headers")

        if headers is None:
            headers = {}
        else:
            headers = dict(headers)

        if not kwargs.get("skip_auth_headers", None):
            auth_headers = await self.get_headers()
            headers.update(auth_headers)

        async with self._request_semaphore:
            for attempt in range(4):
                response = await self.session.request(
                    method, f"{self.host}/{path}", headers=headers, json=json
                )
                if response.status == 429 and attempt < 3:
                    _LOGGER.debug(
                        f"Request rate limited (429), retrying in {2 ** attempt} seconds..."
                    )
                    await asyncio.sleep(2**attempt)
                    continue
                return response
