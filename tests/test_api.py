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
        api_key="mock_api_key",
    )

    token_manager.expire_token()

    async with ClientSession() as session:
        # Create an instance of ElectroluxHubAPI
        hub_api = ElectroluxHubAPI(session, token_manager)

        with aioresponses() as mocked:
            # Mock the response for the token refresh
            refresh_url = "https://api.developer.electrolux.one/api/v1/token/refresh"
            mocked.post(
                refresh_url,
                payload={
                    "accessToken": "new_access_token",
                    "refreshToken": "new_refresh_token",
                },
            )

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
        refresh_token="mock_refresh_token",
    )

    async with ClientSession() as session:
        # Create an instance of ElectroluxHubAPI
        hub_api = ElectroluxHubAPI(session, token_manager)

        with aioresponses() as mocked:
            # Mock the response for the appliances endpoint
            appliances_url = "https://api.developer.electrolux.one/api/v1/appliances"
            mocked.get(
                appliances_url,
                payload=[
                    {
                        "applianceId": "999011524",
                        "applianceName": "My Air Conditioner",
                        "applianceType": "AC",
                        "created": "2022-07-20T08:19:06.521Z",
                    }
                ],
            )

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
        refresh_token="mock_refresh_token",
    )

    async with ClientSession() as session:
        # Create an instance of ElectroluxHubAPI
        hub_api = ElectroluxHubAPI(session, token_manager)

        with aioresponses() as mocked:
            # Mock the response for the specific appliance endpoint
            appliance_id = "999011524_00:94700001-443E070ABC12"
            appliance_url = f"https://api.developer.electrolux.one/api/v1/appliances/{appliance_id}/info"
            mocked.get(
                appliance_url,
                payload={
                    "applianceId": appliance_id,
                    "applianceName": "My Air Conditioner",
                    "applianceType": "AC",
                    "created": "2022-07-20T08:19:06.521Z",
                },
            )

            # Call the method
            appliance = await hub_api.async_get_appliance(appliance_id)

            # Assertions
            assert isinstance(appliance, Appliance)
            assert appliance.id == appliance_id
            assert appliance.name == "My Air Conditioner"
            assert appliance.type == "AC"


@pytest.mark.asyncio
async def test_watch_appliances(monkeypatch):
    from unittest.mock import MagicMock

    token_manager = MockTokenManager(
        api_key="mock_api_key",
        access_token="valid_access_token",
        refresh_token="mock_refresh_token",
    )

    # Mock the aiohttp_sse_client EventSource class
    mock_event1 = MagicMock()
    mock_event1.data = '{"applianceId": "123", "property": "Fanspeed", "value": 3}'
    mock_event2 = MagicMock()
    mock_event2.data = '{"applianceId": "123", "property": "Workmode", "value": "Auto"}'

    mock_event_source_instance = MagicMock()

    class MockAsyncIterator:
        def __init__(self, seq):
            self.iter = iter(seq)

        def __iter__(self):
            return self.iter

        def __aiter__(self):
            return self

        async def __anext__(self):
            try:
                return next(self.iter)
            except StopIteration:
                raise StopAsyncIteration

    # Using simple async generator to mock the iterator
    class BreakLoopException(Exception):
        pass

    class MockEventSource:
        async def __aiter__(self):
            yield mock_event1
            yield mock_event2
            raise BreakLoopException()

    mock_event_source_instance = MockEventSource()

    class AsyncContextManagerMock:
        async def __aenter__(self):
            return mock_event_source_instance

        async def __aexit__(self, exc_type, exc, tb):
            pass

    mock_event_source = MagicMock(return_value=AsyncContextManagerMock())

    monkeypatch.setattr("pyelectroluxgroup.api.EventSource", mock_event_source)

    async with ClientSession() as session:
        hub_api = ElectroluxHubAPI(session, token_manager)

        with aioresponses() as mocked:
            livestream_url = (
                "https://api.developer.electrolux.one/api/v1/configurations/livestream"
            )
            mocked.get(
                livestream_url,
                payload={"url": "https://livestream.developer.electrolux.one/stream"},
            )

            # Call the method and collect the results
            events = []
            try:
                async for event in hub_api.watch_appliances():
                    events.append(event)
            except BreakLoopException:
                pass

            assert len(events) == 2
            assert events[0] == {
                "applianceId": "123",
                "property": "Fanspeed",
                "value": 3,
            }
            assert events[1] == {
                "applianceId": "123",
                "property": "Workmode",
                "value": "Auto",
            }
