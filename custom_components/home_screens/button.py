"""Navigation buttons for Home Screens."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import HomeScreensApiError
from .const import DOMAIN
from .coordinator import HomeScreensCoordinator
from .entity import HomeScreensEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: HomeScreensCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            HomeScreensButton(coordinator, "next_screen", "Next screen", "mdi:skip-next", "next_screen"),
            HomeScreensButton(coordinator, "prev_screen", "Previous screen", "mdi:skip-previous", "prev_screen"),
            HomeScreensButton(coordinator, "clear_alerts", "Clear alerts", "mdi:bell-off", "clear_alerts"),
        ]
    )


class HomeScreensButton(HomeScreensEntity, ButtonEntity):
    def __init__(self, coordinator: HomeScreensCoordinator, key: str, name: str, icon: str, client_method: str) -> None:
        super().__init__(coordinator, key)
        self._attr_name = name
        self._attr_icon = icon
        self._client_method = client_method

    async def async_press(self) -> None:
        method = getattr(self.coordinator.client, self._client_method)
        try:
            await method()
        except HomeScreensApiError as err:
            raise HomeAssistantError(str(err)) from err
        await self.coordinator.async_request_refresh()
