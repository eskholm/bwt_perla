from __future__ import annotations
import voluptuous as vol
import aiohttp
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from .const import DOMAIN, CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD, CONF_SCAN_INTERVAL, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, API_PATH

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): str,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
    vol.Optional(CONF_USERNAME): str,
    vol.Optional(CONF_PASSWORD): str,
    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
})

async def _probe(host: str, port: int | None, username: str | None, password: str | None) -> dict:
    base = f"http://{host}:{port}" if port else f"http://{host}"
    url = f"{base}{API_PATH}"
    auth = aiohttp.BasicAuth(username, password) if username else None
    async with aiohttp.ClientSession() as session:
        async with session.get(url, auth=auth) as resp:
            if resp.status != 200:
                raise RuntimeError(f"HTTP {resp.status}")
            return await resp.json(content_type=None)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA)

        host = user_input[CONF_HOST].strip()
        await self.async_set_unique_id(f"{DOMAIN}_{host}")
        self._abort_if_unique_id_configured()

        try:
            await _probe(host, user_input.get(CONF_PORT), user_input.get(CONF_USERNAME), user_input.get(CONF_PASSWORD))
        except Exception as e:
            return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA,
                                        errors={"base": "cannot_connect"})

        return self.async_create_entry(title=f"BWT Perla ({host})", data=user_input)
