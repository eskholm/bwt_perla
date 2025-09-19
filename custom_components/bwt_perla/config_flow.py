from __future__ import annotations

from typing import Any

import voluptuous as vol
from aiohttp import ClientError, BasicAuth
import async_timeout

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    API_PATH,
    CONF_HOST,
    CONF_PORT,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=8080): vol.Coerce(int),
        vol.Optional(CONF_USERNAME, default=""): str,
        vol.Optional(CONF_PASSWORD, default=""): str,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=5, max=3600)
        ),
    }
)


async def _try_connect(hass: HomeAssistant, host: str, port: int | None, username: str, password: str) -> dict[str, Any]:
    base = f"http://{host}:{port}" if port else f"http://{host}"
    url = f"{base}{API_PATH}"
    session = async_get_clientsession(hass)
    auth = BasicAuth(username, password) if username else None
    try:
        async with async_timeout.timeout(10):
            resp = await session.get(url, auth=auth)
        if resp.status != 200:
            txt = await resp.text()
            raise ClientError(f"HTTP {resp.status}: {txt[:200]}")
        # Nogle enheder sætter ikke content-type til application/json
        data = await resp.json(content_type=None)
        if not isinstance(data, dict):
            raise ClientError("Unexpected payload")
        return data
    except Exception as err:
        raise ClientError(str(err)) from err


class BwtPerlaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = user_input.get(CONF_PORT)
            username = user_input.get(CONF_USERNAME, "").strip()
            password = user_input.get(CONF_PASSWORD, "")

            # unik pr. host:port
            unique = f"{host}:{port or 80}"
            await self.async_set_unique_id(unique)
            self._abort_if_unique_id_configured()

            try:
                await _try_connect(self.hass, host, port, username, password)
            except ClientError:
                errors["base"] = "cannot_connect"

            if not errors:
                return self.async_create_entry(title="BWT Perla", data=user_input)

        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors=errors)
