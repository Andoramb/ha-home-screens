"""Represents the Home Screens display as a dimmable light.

on/off maps to wake/sleep, brightness (0-255 in HA, 0-100 on the device)
maps to POST /api/display/brightness.
"""
from __future__ import annotations

from typing import Any

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.color import brightness_to_value, value_to_brightness

from .api import HomeScreensApiError
from .const import DISPLAY_STATE_ASLEEP, DOMAIN
from .coordinator import HomeScreensCoordinator
from .entity import HomeScreensEntity

BRIGHTNESS_SCALE = (1, 100)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: HomeScreensCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HomeScreensDisplayLight(coordinator)])


class HomeScreensDisplayLight(HomeScreensEntity, LightEntity):
    """The physical display, controllable like a dimmable light."""

    _attr_translation_key = "display"
    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_icon = "mdi:monitor-dashboard"

    def __init__(self, coordinator: HomeScreensCoordinator) -> None:
        super().__init__(coordinator, "display")

    @property
    def is_on(self) -> bool:
        return self._status.get("displayState") != DISPLAY_STATE_ASLEEP

    @property
    def brightness(self) -> int | None:
        value = self._status.get("brightness")
        if value is None:
            return None
        return round(value_to_brightness(BRIGHTNESS_SCALE, value))

    async def async_turn_on(self, **kwargs: Any) -> None:
        client = self.coordinator.client
        try:
            await client.wake()
            if (brightness := kwargs.get("brightness")) is not None:
                device_value = round(brightness_to_value(BRIGHTNESS_SCALE, brightness))
                await client.set_brightness(device_value)
        except HomeScreensApiError as err:
            raise HomeAssistantError(str(err)) from err
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        try:
            await self.coordinator.client.sleep()
        except HomeScreensApiError as err:
            raise HomeAssistantError(str(err)) from err
        await self.coordinator.async_request_refresh()
