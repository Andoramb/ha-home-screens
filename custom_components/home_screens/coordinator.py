"""DataUpdateCoordinator for the Home Screens integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import HomeScreensApiError, HomeScreensClient
from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class HomeScreensCoordinator(DataUpdateCoordinator[dict]):
    """Fetches /api/display/status and /api/config and merges them."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: HomeScreensClient) -> None:
        self.entry = entry
        self.client = client
        scan_interval = entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            name="home_screens",
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict:
        try:
            status = await self.client.status()
            config = await self.client.config()
        except HomeScreensApiError as err:
            raise UpdateFailed(str(err)) from err

        return {
            "status": status,
            "config": config,
            "screens": config.get("screens", []),
            "profiles": config.get("profiles", []),
        }

    def modules(self) -> list[dict]:
        """Flatten every module instance across all screens."""
        result = []
        for screen in self.data.get("screens", []) if self.data else []:
            for module in screen.get("modules", []):
                result.append(
                    {
                        "id": module.get("id"),
                        "type": module.get("type"),
                        "title": (module.get("style") or {}).get("title"),
                        "enabled": module.get("enabled", True),
                        "screen_id": screen.get("id"),
                        "screen_name": screen.get("name"),
                    }
                )
        return result
