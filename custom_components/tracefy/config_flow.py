"""Config flow for Tracefy integration."""
import logging

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import TracefyApi, TracefyAuthError, TracefyApiError
from .const import DOMAIN, CONF_EMAIL, CONF_PASSWORD

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


async def _validate_credentials(hass: HomeAssistant, email: str, password: str) -> list[dict]:
    """Try to authenticate and return first page of entities."""
    session = async_get_clientsession(hass)
    api = TracefyApi(email, password, session)
    return await api.get_entities()


class TracefyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow: step 1 = credentials, step 2 = pick device (if multiple)."""

    VERSION = 1

    def __init__(self):
        self._email: str = ""
        self._password: str = ""
        self._entities: list[dict] = []

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Show login form and validate credentials."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._email = user_input[CONF_EMAIL].strip()
            self._password = user_input[CONF_PASSWORD]

            try:
                self._entities = await _validate_credentials(
                    self.hass, self._email, self._password
                )
            except TracefyAuthError:
                errors["base"] = "invalid_auth"
            except TracefyApiError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error during Tracefy login")
                errors["base"] = "unknown"
            else:
                # Prevent duplicate entries for same account
                await self.async_set_unique_id(self._email.lower())
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Tracefy ({self._email})",
                    data={
                        CONF_EMAIL: self._email,
                        CONF_PASSWORD: self._password,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(self, user_input: dict | None = None) -> FlowResult:
        """Re-authenticate when the token has become invalid."""
        return await self.async_step_user()
