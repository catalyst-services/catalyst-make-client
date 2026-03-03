"""Make.com API client."""

import os
from pathlib import Path

import aiohttp

from .models import Execution, Organization, Scenario


class MakeClient:
    """Async Make.com API client."""

    BASE_URL = "https://www.make.com/api/v2"

    def __init__(self, token: str | None = None):
        """Initialize Make.com client.

        Args:
            token: API token. If not provided, reads from MAKE_API_KEY env var
                  or ~/.catalyst_make_key file.
        """
        self.token = token or self._load_token()
        self.session: aiohttp.ClientSession | None = None

    def _load_token(self) -> str:
        """Load API token from environment or file."""
        # Check environment variable
        if token := os.getenv("MAKE_API_KEY"):
            return token

        # Check home directory
        key_file = Path.home() / ".catalyst_make_key"
        if key_file.exists():
            return key_file.read_text().strip()

        msg = (
            "MAKE_API_KEY not found. Set MAKE_API_KEY env var or "
            "create ~/.catalyst_make_key file"
        )
        raise ValueError(msg)

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def _request(self, method: str, endpoint: str, **kwargs):
        """Make authenticated request to Make.com API."""
        if not self.session:
            msg = "Client not initialized. Use 'async with' context manager."
            raise RuntimeError(msg)

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        headers.update(kwargs.pop("headers", {}))

        url = f"{self.BASE_URL}{endpoint}"
        async with self.session.request(
            method, url, headers=headers, **kwargs
        ) as resp:
            if resp.status == 401:
                raise ValueError("Invalid API token")
            if resp.status >= 400:
                msg = f"API error {resp.status}: {await resp.text()}"
                raise RuntimeError(msg)
            return await resp.json()

    async def get_organization(self) -> Organization:
        """Get current organization."""
        data = await self._request("GET", "/organizations/me")
        return Organization(**data)

    async def list_scenarios(self, limit: int = 100) -> list[Scenario]:
        """List all scenarios."""
        data = await self._request("GET", "/scenarios", params={"limit": limit})
        scenarios = data.get("scenarios", [])
        return [Scenario(**s) for s in scenarios]

    async def get_scenario(self, scenario_id: int) -> Scenario:
        """Get a specific scenario."""
        data = await self._request("GET", f"/scenarios/{scenario_id}")
        return Scenario(**data)

    async def list_executions(
        self, scenario_id: int, limit: int = 50
    ) -> list[Execution]:
        """List executions for a scenario."""
        data = await self._request(
            "GET", f"/scenarios/{scenario_id}/executions", params={"limit": limit}
        )
        executions = data.get("executions", [])
        return [Execution(**e) for e in executions]

    async def test_connection(self) -> bool:
        """Test API connection."""
        try:
            await self.get_organization()
            return True
        except Exception:  # noqa: BLE001
            return False
