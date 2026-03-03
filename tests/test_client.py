"""Tests for Make.com API client."""

import pytest
from unittest.mock import AsyncMock, patch

from src.catalyst_make_client.client import MakeClient
from src.catalyst_make_client.models import Organization, Scenario


@pytest.mark.asyncio
async def test_client_initialization():
    """Test client can be initialized with token."""
    client = MakeClient(token="test_token_123")
    assert client.token == "test_token_123"


@pytest.mark.asyncio
async def test_client_context_manager():
    """Test client as async context manager."""
    async with MakeClient(token="test_token") as client:
        assert client.session is not None


@pytest.mark.asyncio
async def test_token_loading_from_env(monkeypatch):
    """Test loading token from environment variable."""
    monkeypatch.setenv("MAKE_API_KEY", "env_token_123")
    client = MakeClient()
    assert client.token == "env_token_123"


@pytest.mark.asyncio
async def test_token_loading_missing():
    """Test error when token is missing."""
    import os

    # Ensure env var is not set
    if "MAKE_API_KEY" in os.environ:
        del os.environ["MAKE_API_KEY"]

    with pytest.raises(ValueError, match="MAKE_API_KEY not found"):
        MakeClient()


@pytest.mark.asyncio
async def test_get_organization():
    """Test getting organization."""
    with patch("aiohttp.ClientSession") as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value = mock_session

        # Mock the response
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(
            return_value={"id": 1, "name": "Test Organization"}
        )
        mock_session.request.return_value.__aenter__.return_value = mock_resp

        async with MakeClient(token="test_token") as client:
            org = await client.get_organization()
            assert isinstance(org, Organization)
            assert org.name == "Test Organization"


@pytest.mark.asyncio
async def test_list_scenarios():
    """Test listing scenarios."""
    with patch("aiohttp.ClientSession") as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value = mock_session

        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(
            return_value={
                "scenarios": [
                    {"id": 1, "name": "Lead Capture", "enabled": True},
                    {"id": 2, "name": "Invoice Gen", "enabled": True},
                ]
            }
        )
        mock_session.request.return_value.__aenter__.return_value = mock_resp

        async with MakeClient(token="test_token") as client:
            scenarios = await client.list_scenarios()
            assert len(scenarios) == 2
            assert scenarios[0].name == "Lead Capture"
            assert all(isinstance(s, Scenario) for s in scenarios)


@pytest.mark.asyncio
async def test_api_error_handling():
    """Test error handling for API errors."""
    with patch("aiohttp.ClientSession") as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value = mock_session

        mock_resp = AsyncMock()
        mock_resp.status = 401
        mock_session.request.return_value.__aenter__.return_value = mock_resp

        async with MakeClient(token="bad_token") as client:
            with pytest.raises(ValueError, match="Invalid API token"):
                await client.get_organization()


@pytest.mark.asyncio
async def test_test_connection_success():
    """Test connection test succeeds."""
    with patch("aiohttp.ClientSession") as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value = mock_session

        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value={"id": 1, "name": "Org"})
        mock_session.request.return_value.__aenter__.return_value = mock_resp

        async with MakeClient(token="test_token") as client:
            result = await client.test_connection()
            assert result is True


@pytest.mark.asyncio
async def test_test_connection_failure():
    """Test connection test fails gracefully."""
    with patch("aiohttp.ClientSession") as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value = mock_session

        mock_resp = AsyncMock()
        mock_resp.status = 500
        mock_resp.text = AsyncMock(return_value="Server error")
        mock_session.request.return_value.__aenter__.return_value = mock_resp

        async with MakeClient(token="test_token") as client:
            result = await client.test_connection()
            assert result is False
