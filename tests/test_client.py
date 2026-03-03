"""Tests for Make.com API client."""

import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

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
async def test_token_loading_missing(monkeypatch):
    """Test error when token is missing."""
    # Ensure env var is not set
    monkeypatch.delenv("MAKE_API_KEY", raising=False)
    # Mock home directory to avoid reading real file
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("HOME", tmpdir)
        with pytest.raises(ValueError, match="MAKE_API_KEY not found"):
            MakeClient()


@pytest.mark.asyncio
async def test_get_organization():
    """Test getting organization."""
    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"id": 1, "name": "Test Organization"})

    with patch("aiohttp.ClientSession") as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value = mock_session
        mock_session.request = MagicMock()
        mock_session.request.return_value.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session.request.return_value.__aexit__ = AsyncMock(return_value=None)

        async with MakeClient(token="test_token") as client:
            org = await client.get_organization()
            assert isinstance(org, Organization)
            assert org.name == "Test Organization"


@pytest.mark.asyncio
async def test_list_scenarios():
    """Test listing scenarios."""
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

    with patch("aiohttp.ClientSession") as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value = mock_session
        mock_session.request = MagicMock()
        mock_session.request.return_value.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session.request.return_value.__aexit__ = AsyncMock(return_value=None)

        async with MakeClient(token="test_token") as client:
            scenarios = await client.list_scenarios()
            assert len(scenarios) == 2
            assert scenarios[0].name == "Lead Capture"
            assert all(isinstance(s, Scenario) for s in scenarios)


@pytest.mark.asyncio
async def test_api_error_handling():
    """Test error handling for API errors."""
    mock_resp = AsyncMock()
    mock_resp.status = 401

    with patch("aiohttp.ClientSession") as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value = mock_session
        mock_session.request = MagicMock()
        mock_session.request.return_value.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session.request.return_value.__aexit__ = AsyncMock(return_value=None)

        async with MakeClient(token="bad_token") as client:
            with pytest.raises(ValueError, match="Invalid API token"):
                await client.get_organization()


@pytest.mark.asyncio
async def test_test_connection_success():
    """Test connection test succeeds."""
    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"id": 1, "name": "Org"})

    with patch("aiohttp.ClientSession") as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value = mock_session
        mock_session.request = MagicMock()
        mock_session.request.return_value.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session.request.return_value.__aexit__ = AsyncMock(return_value=None)

        async with MakeClient(token="test_token") as client:
            result = await client.test_connection()
            assert result is True


@pytest.mark.asyncio
async def test_test_connection_failure():
    """Test connection test fails gracefully."""
    mock_resp = AsyncMock()
    mock_resp.status = 500
    mock_resp.text = AsyncMock(return_value="Server error")

    with patch("aiohttp.ClientSession") as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value = mock_session
        mock_session.request = MagicMock()
        mock_session.request.return_value.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session.request.return_value.__aexit__ = AsyncMock(return_value=None)

        async with MakeClient(token="test_token") as client:
            result = await client.test_connection()
            assert result is False
