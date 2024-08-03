from aiohttp import ClientSession, ClientResponse


class Auth:
    """Class to make authenticated requests."""

    def __init__(self, websession: ClientSession, host: str, access_token: str, api_key: str):
        """Initialize the auth."""
        self.websession = websession
        self.host = host
        self.access_token = access_token
        self.api_key = api_key

    async def request(self, method: str, path: str, **kwargs) -> ClientResponse:
        """Make a request."""
        headers = kwargs.get("headers")

        if headers is None:
            headers = {}
        else:
            headers = dict(headers)

        headers["authorization"] = f"Bearer {self.access_token}"
        headers["x-api-key"] = self.api_key

        return await self.websession.request(
            method, f"{self.host}/{path}", headers=headers,
        )