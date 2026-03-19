from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt

from pyelectroluxgroup.token_manager import TokenManager


class ConcreteTokenManager(TokenManager):
    """Concrete implementation of TokenManager for testing."""

    def __init__(self, access_token: str, refresh_token: str, api_key: str):
        super().__init__(access_token, refresh_token, api_key)

    def update(self, access_token: str, refresh_token: str, api_key: str | None = None):
        super().update(access_token, refresh_token, api_key)


def test_is_token_valid_when_expired():
    """Test that a token with less than 10 minutes to expiry is invalid."""
    token_manager = ConcreteTokenManager("access_token", "refresh_token", "api_key")

    # Mock current time in UTC
    mock_now_utc = datetime(2024, 3, 31, 1, 55, 0, tzinfo=timezone.utc)

    # Expiration is in 5 minutes (less than 10)
    mock_exp_utc = mock_now_utc + timedelta(minutes=5)
    exp_timestamp = mock_exp_utc.timestamp()

    with patch("pyelectroluxgroup.token_manager.datetime") as mock_datetime:
        # We need to mock datetime.now to return our fixed time
        mock_datetime.now.return_value = mock_now_utc
        # We need to pass through fromtimestamp since the original code uses it
        mock_datetime.fromtimestamp.side_effect = datetime.fromtimestamp

        with patch("pyelectroluxgroup.token_manager.jwt.decode") as mock_jwt_decode:
            mock_jwt_decode.return_value = {"exp": exp_timestamp}

            # Since it expires in 5 minutes, it should return False
            assert token_manager.is_token_valid() is False


def test_is_token_valid_when_valid():
    """Test that a token with more than 10 minutes to expiry is valid."""
    token_manager = ConcreteTokenManager("access_token", "refresh_token", "api_key")

    # Mock current time in UTC
    mock_now_utc = datetime(2024, 3, 31, 1, 55, 0, tzinfo=timezone.utc)

    # Expiration is in 15 minutes (more than 10)
    mock_exp_utc = mock_now_utc + timedelta(minutes=15)
    exp_timestamp = mock_exp_utc.timestamp()

    with patch("pyelectroluxgroup.token_manager.datetime") as mock_datetime:
        mock_datetime.now.return_value = mock_now_utc
        mock_datetime.fromtimestamp.side_effect = datetime.fromtimestamp

        with patch("pyelectroluxgroup.token_manager.jwt.decode") as mock_jwt_decode:
            mock_jwt_decode.return_value = {"exp": exp_timestamp}

            # Since it expires in 15 minutes, it should return True
            assert token_manager.is_token_valid() is True


def test_is_token_valid_handles_expired_signature():
    """Test that if jwt.decode raises ExpiredSignatureError, token is invalid."""
    token_manager = ConcreteTokenManager("access_token", "refresh_token", "api_key")

    with patch(
        "pyelectroluxgroup.token_manager.jwt.decode",
        side_effect=jwt.ExpiredSignatureError,
    ):
        assert token_manager.is_token_valid() is False
