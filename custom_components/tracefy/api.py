"""Tracefy API client."""
import logging
from datetime import datetime, timedelta

import aiohttp

from .const import AUTH_URL, API_URL, CLIENT_ID, AUDIENCE

_LOGGER = logging.getLogger(__name__)


class TracefyAuthError(Exception):
    """Authentication failed."""


class TracefyApiError(Exception):
    """API error."""


class TracefyApi:
    """Tracefy API client."""

    def __init__(self, email: str, password: str, session: aiohttp.ClientSession):
        self._email = email
        self._password = password
        self._session = session
        self._access_token: str | None = None
        self._token_expires: datetime = datetime.min

    async def authenticate(self) -> str:
        """Get a valid access token, refreshing if needed."""
        if self._access_token and datetime.now() < self._token_expires - timedelta(minutes=5):
            return self._access_token

        payload = {
            "client_id": CLIENT_ID,
            "username": self._email,
            "password": self._password,
            "grant_type": "password",
            "scope": "openid profile email phone address",
            "audience": AUDIENCE,
        }

        try:
            async with self._session.post(AUTH_URL, json=payload, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 403:
                    raise TracefyAuthError("Invalid credentials")
                if resp.status != 200:
                    text = await resp.text()
                    raise TracefyAuthError(f"Auth failed ({resp.status}): {text}")
                data = await resp.json()
        except aiohttp.ClientError as err:
            raise TracefyApiError(f"Network error during auth: {err}") from err

        if "access_token" not in data:
            raise TracefyAuthError("No access_token in response")

        self._access_token = data["access_token"]
        expires_in = data.get("expires_in", 86400)
        self._token_expires = datetime.now() + timedelta(seconds=expires_in)
        _LOGGER.debug("Tracefy: authenticated successfully")
        return self._access_token

    async def get_entities(self) -> list[dict]:
        """Fetch all entities (bikes/trackers) for this account."""
        token = await self.authenticate()
        headers = {"Authorization": f"Bearer {token}"}

        try:
            async with self._session.get(API_URL, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 401:
                    self._access_token = None
                    raise TracefyAuthError("Token rejected by API")
                if resp.status != 200:
                    text = await resp.text()
                    raise TracefyApiError(f"API error ({resp.status}): {text}")
                data = await resp.json()
        except aiohttp.ClientError as err:
            raise TracefyApiError(f"Network error: {err}") from err

        if not data.get("success"):
            raise TracefyApiError(f"API returned success=false: {data.get('message')}")

        return data.get("data", [])
