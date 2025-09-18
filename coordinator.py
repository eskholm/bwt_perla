from __future__ import annotations

from typing import Any
from datetime import timedelta
import logging

import async_timeout
from aiohttp import BasicAuth
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DEFAULT_SCAN_INTERVAL,
    API_PATH,
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class BwtCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, conf: dict):
        self.hass = hass
        self._host = conf[CONF_HOST].strip().rstrip("/")
        self._port = conf.get(CONF_PORT)
        self._username = conf.get(CONF_USERNAME)
        self._password = conf.get(CONF_PASSWORD)

        base = f"http://{self._host}:{self._port}" if self._port else f"http://{self._host}"
        self._url = f"{base}{API_PATH}"

        interval = timedelta(seconds=conf.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))

        super().__init__(
            hass,
            _LOGGER,
            name="BWT Perla Coordinator",
            update_interval=interval,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            auth = BasicAuth(self._username, self._password) if self._username else None
            session = async_get_clientsession(self.hass)
            async with async_timeout.timeout(10):
                resp = await session.get(self._url, auth=auth)
                if resp.status != 200:
                    text = await resp.text()
                    raise UpdateFailed(f"HTTP {resp.status}: {text[:200]}")
                # BWT kan mangle content-type; slå kontrol fra
                data = await resp.json(content_type=None)
                if not isinstance(data, dict):
                    raise UpdateFailed("Unexpected payload type")
                return data
        except Exception as err:
            raise UpdateFailed(str(err)) from err
