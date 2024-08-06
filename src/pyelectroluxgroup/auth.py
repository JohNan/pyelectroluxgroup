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
        api_key: str,
        async_get_access_token: Callable,
    ):
        """Initialize the auth."""
        self.session = session
        self.host = host
        self.api_key = api_key
        self.async_get_access_token = async_get_access_token

    async def request(self, method: str, path: str, **kwargs) -> ClientResponse:
        """Make a request."""
        json = kwargs.get("json", None)
        headers = kwargs.get("headers")

        if headers is None:
            headers = {}
        else:
            headers = dict(headers)

        if not kwargs.get("skip_auth_headers", None):
            access_token = await self.async_get_access_token()
            headers["authorization"] = f"Bearer {access_token}"
            headers["x-api-key"] = self.api_key

        return await self.session.request(
            method, f"{self.host}/{path}", headers=headers, json=json
        )
