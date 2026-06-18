"""Tracefy DataUpdateCoordinator."""
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import TracefyApi, TracefyAuthError, TracefyApiError
from .const import DOMAIN, SCAN_INTERVAL_MINUTES

_LOGGER = logging.getLogger(__name__)


class TracefyCoordinator(DataUpdateCoordinator):
    """Fetch data from Tracefy API on a schedule."""

    def __init__(self, hass: HomeAssistant, api: TracefyApi, entry: ConfigEntry) -> None:
        self.api = api
        self.entry = entry
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=SCAN_INTERVAL_MINUTES),
        )

    async def _async_update_data(self) -> dict:
        """Fetch entities and return keyed by entity id."""
        try:
            entities = await self.api.get_entities()
        except TracefyAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except TracefyApiError as err:
            raise UpdateFailed(str(err)) from err

        return {e["id"]: e for e in entities}
