import pytest
from aiohttp import ClientSession
from aioresponses import aioresponses

from pyelectroluxgroup.api import ElectroluxHubAPI
from pyelectroluxgroup.appliance import Appliance
from pyelectroluxgroup.token_manager import TokenManager


class MockTokenManager(TokenManager):
    """Mock implementation of the TokenManager for testing."""

    def __init__(self, access_token: str, refresh_token: str, api_key: str):
        super().__init__(access_token, refresh_token, api_key)
        self.token_valid = True

    def update(self, access_token: str, refresh_token: str, api_key: str | None = None):
        super().update(access_token, refresh_token, api_key)

    def is_token_valid(self) -> bool:
        return self.token_valid

    def expire_token(self):
        """Expire the token to simulate an expired access token."""
        self.token_valid = False


@pytest.mark.asyncio
async def test_async_get_access_token():
    # Mock the token manager with an expired access token
    token_manager = MockTokenManager(
        access_token="expired_access_token",
        refresh_token="mock_refresh_token",
        api_key="mock_api_key"
    )

    token_manager.expire_token()

    async with ClientSession() as session:
        # Create an instance of ElectroluxHubAPI
        hub_api = ElectroluxHubAPI(session, token_manager)

        with aioresponses() as mocked:
            # Mock the response for the token refresh
            refresh_url = "https://api.developer.electrolux.one/api/v1/token/refresh"
            mocked.post(refresh_url, payload={"accessToken": "new_access_token", "refreshToken": "new_refresh_token"})

            # Call the method
            access_token = await hub_api.async_get_access_token()

            # Assertions
            assert access_token == "new_access_token"
            assert token_manager.access_token == "new_access_token"
            assert token_manager.refresh_token == "new_refresh_token"


@pytest.mark.asyncio
async def test_async_get_appliances():
    # Mock the token manager
    token_manager = MockTokenManager(
        api_key="mock_api_key",
        access_token="valid_access_token",
        refresh_token="mock_refresh_token"
    )

    async with ClientSession() as session:
        # Create an instance of ElectroluxHubAPI
        hub_api = ElectroluxHubAPI(session, token_manager)

        with aioresponses() as mocked:
            # Mock the response for the appliances endpoint
            appliances_url = "https://api.developer.electrolux.one/api/v1/appliances"
            mocked.get(appliances_url, payload=[
                {
                    "applianceId": "999011524",
                    "applianceName": "My Air Conditioner",
                    "applianceType": "AC",
                    "created": "2022-07-20T08:19:06.521Z"
                }
            ])

            # Call the method
            appliances = await hub_api.async_get_appliances()

            # Assertions
            assert len(appliances) == 1
            assert isinstance(appliances[0], Appliance)
            assert appliances[0].id == "999011524"
            assert appliances[0].name == "My Air Conditioner"
            assert appliances[0].type == "AC"


@pytest.mark.asyncio
async def test_async_get_appliance():
    # Mock the token manager
    token_manager = MockTokenManager(
        api_key="mock_api_key",
        access_token="valid_access_token",
        refresh_token="mock_refresh_token"
    )

    async with ClientSession() as session:
        # Create an instance of ElectroluxHubAPI
        hub_api = ElectroluxHubAPI(session, token_manager)

        with aioresponses() as mocked:
            # Mock the response for the specific appliance endpoint
            appliance_id = "999011524_00:94700001-443E070ABC12"
            appliance_url = f"https://api.developer.electrolux.one/api/v1/appliances/{appliance_id}/info"
            mocked.get(appliance_url, payload={
                "applianceId": appliance_id,
                "applianceName": "My Air Conditioner",
                "applianceType": "AC",
                "created": "2022-07-20T08:19:06.521Z"
            })

            # Call the method
            appliance = await hub_api.async_get_appliance(appliance_id)

            # Assertions
            assert isinstance(appliance, Appliance)
            assert appliance.id == appliance_id
            assert appliance.name == "My Air Conditioner"
            assert appliance.type == "AC"
