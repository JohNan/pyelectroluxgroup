import pytest
from unittest.mock import AsyncMock, MagicMock

from aioresponses import aioresponses
from aiohttp import ClientSession
from yarl import URL

from pyelectroluxgroup.auth import Auth


@pytest.mark.asyncio
async def test_auth_request_with_auth_headers():
    # Mock the async_get_access_token callable
    mock_get_access_token = AsyncMock(return_value="mock_access_token")

    async with ClientSession() as session:
        # Initialize the Auth object
        auth = Auth(
            session=session,
            host="https://api.developer.electrolux.one/api/v1",
            api_key="mock_api_key",
            async_get_access_token=mock_get_access_token
        )

        with aioresponses() as mocked:
            # Mock the API response
            url = "https://api.developer.electrolux.one/api/v1/test-endpoint"
            mocked.get(url, status=200, payload={"key": "value"})

            # Make a request using the Auth class
            response = await auth.request("get", "test-endpoint")

            # Assertions
            assert response.status == 200
            json_response = await response.json()
            assert json_response == {"key": "value"}

            # Check if headers were correctly set
            mock_get_access_token.assert_called_once()

            # Extract and verify the headers from the mock requests
            request_entry = mocked.requests.get(("get", URL(url)))
            request_headers = request_entry[0].kwargs["headers"]
            assert request_headers["authorization"] == "Bearer mock_access_token"
            assert request_headers["x-api-key"] == "mock_api_key"


@pytest.mark.asyncio
async def test_auth_request_without_auth_headers():
    # Mock the async_get_access_token callable
    mock_get_access_token = MagicMock()

    async with ClientSession() as session:
        # Initialize the Auth object
        auth = Auth(
            session=session,
            host="https://api.developer.electrolux.one/api/v1",
            api_key="mock_api_key",
            async_get_access_token=mock_get_access_token
        )

        with aioresponses() as mocked:
            # Mock the API response
            url = "https://api.developer.electrolux.one/api/v1/test-endpoint"
            mocked.get(url, status=200,
                       payload={"key": "value"})

            # Make a request without auth headers
            response = await auth.request("get", "test-endpoint", skip_auth_headers=True)

            # Assertions
            assert response.status == 200
            json_response = await response.json()
            assert json_response == {"key": "value"}

            # Ensure async_get_access_token was not called
            mock_get_access_token.assert_not_called()

            # Check if headers were not set
            request_entry = mocked.requests.get(("get", URL(url)))
            request_headers = request_entry[0].kwargs["headers"]
            assert "authorization" not in request_headers
            assert "x-api-key" not in request_headers


@pytest.mark.asyncio
async def test_auth_request_with_custom_headers():
    # Mock the async_get_access_token callable
    mock_get_access_token = AsyncMock(return_value="mock_access_token")

    async with ClientSession() as session:
        # Initialize the Auth object
        auth = Auth(
            session=session,
            host="https://api.developer.electrolux.one/api/v1",
            api_key="mock_api_key",
            async_get_access_token=mock_get_access_token
        )

        with aioresponses() as mocked:
            # Mock the API response
            url = "https://api.developer.electrolux.one/api/v1/test-endpoint"
            mocked.get(url, status=200,
                       payload={"key": "value"})

            # Make a request with custom headers
            custom_headers = {"custom-header": "custom_value"}
            response = await auth.request("get", "test-endpoint", headers=custom_headers)

            # Assertions
            assert response.status == 200
            json_response = await response.json()
            assert json_response == {"key": "value"}

            # Ensure async_get_access_token was called
            mock_get_access_token.assert_called_once()

            # Check if custom and auth headers were correctly set
            request_entry = mocked.requests.get(("get", URL(url)))
            request_headers = request_entry[0].kwargs["headers"]
            assert request_headers["custom-header"] == "custom_value"
            assert request_headers["authorization"] == "Bearer mock_access_token"
            assert request_headers["x-api-key"] == "mock_api_key"
